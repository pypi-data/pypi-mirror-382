# © Copyright Databand.ai, an IBM Company 2022
from __future__ import absolute_import, division, print_function, unicode_literals

import contextlib
import logging
import os
import typing

from airflow import DAG
from airflow.configuration import conf as airflow_conf
from airflow.models import DagPickle, DagRun, Pool, TaskInstance
from airflow.utils import timezone
from airflow.utils.db import create_session, provide_session
from airflow.utils.state import State
from sqlalchemy.orm import Session

from dbnd import dbnd_config
from dbnd._core.current import is_verbose
from dbnd._core.errors import DatabandError
from dbnd._core.log.logging_utils import PrefixLoggerAdapter
from dbnd._core.utils.basics.pickle_non_pickable import ready_for_pickle
from dbnd_run import errors
from dbnd_run.airflow.compat import (
    AIRFLOW_VERSION_1,
    AIRFLOW_VERSION_2,
    AIRFLOW_VERSION_AFTER_2_2,
)
from dbnd_run.airflow.compat.airflow_multi_version_shim import (
    LocalExecutor,
    SequentialExecutor,
    get_airflow_conf_log_folder,
)
from dbnd_run.airflow.config import AirflowConfig, get_dbnd_default_args
from dbnd_run.airflow.db_utils import remove_listener_by_name
from dbnd_run.airflow.dbnd_task_executor.airflow_operator_as_dbnd import (
    AirflowDagAsDbndTask,
    AirflowOperatorAsDbndTask,
)
from dbnd_run.airflow.dbnd_task_executor.converters import operator_to_to_dbnd_task_id
from dbnd_run.airflow.dbnd_task_executor.dbnd_task_to_airflow_operator import (
    build_dbnd_operator_from_taskrun,
    set_af_operator_doc_md,
)
from dbnd_run.airflow.dbnd_task_executor.task_instance_state_manager import (
    AirflowTaskInstanceStateManager,
)
from dbnd_run.airflow.executors import AirflowTaskExecutorType
from dbnd_run.airflow.executors.simple_executor import InProcessExecutor
from dbnd_run.airflow.scheduler import airflow_to_databand_sync
from dbnd_run.airflow.scheduler.airflow_to_databand_sync import (
    report_airflow_task_instance,
)
from dbnd_run.airflow.scheduler.dagrun_zombies import fix_zombie_dagrun_task_instances
from dbnd_run.airflow.utils import create_airflow_pool
from dbnd_run.current import is_killed
from dbnd_run.plugin.dbnd_plugins import assert_plugin_enabled
from dbnd_run.run_executor_engine import RunExecutorEngine


if typing.TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

DAG_UNPICKABLE_PROPERTIES = (
    "_log",
    ("user_defined_macros", {}),
    ("user_defined_filters", {}),
    ("params", {}),
)


def compute_log_filepath_from_ti(ti, execution_date) -> str:
    iso = execution_date.isoformat()
    log_folder = get_airflow_conf_log_folder()
    log = os.path.expanduser(log_folder)
    return f"{log}/{ti.dag_id}/{ti.task_id}/{iso}/{ti.try_number}.log"


@provide_session
def create_dagrun_from_dbnd_run(
    databand_run,
    dag,
    execution_date,
    run_id,
    state=State.RUNNING,
    external_trigger=False,
    conf=None,
    session=None,
):
    """
    Create new DagRun and all relevant TaskInstances
    """
    dagrun = (
        session.query(DagRun)
        .filter(DagRun.dag_id == dag.dag_id, DagRun.execution_date == execution_date)
        .first()
    )
    if dagrun is None:
        if AIRFLOW_VERSION_2:
            from airflow.utils.types import DagRunType

            version_specific_params = dict(
                state=state, run_type=DagRunType.BACKFILL_JOB
            )
        else:
            version_specific_params = dict(_state=state)
        dagrun = DagRun(
            run_id=run_id,
            execution_date=execution_date,
            start_date=dag.start_date,
            external_trigger=external_trigger,
            dag_id=dag.dag_id,
            conf=conf,
            **version_specific_params,
        )
        session.add(dagrun)
    else:
        logger.warning("Running with existing airflow dag run %s", dagrun)

    dagrun.dag = dag
    dagrun.run_id = run_id
    session.commit()

    # create the associated task instances
    # state is None at the moment of creation

    # dagrun.verify_integrity(session=session)
    # fetches [TaskInstance] again
    # tasks_skipped = databand_run.tasks_skipped

    # we can find a source of the completion, but also,
    # sometimes we don't know the source of the "complete"
    TI = TaskInstance
    tis = (
        session.query(TI)
        .filter(TI.dag_id == dag.dag_id, TI.execution_date == execution_date)
        .all()
    )
    tis = {ti.task_id: ti for ti in tis}

    logger.info("Tasks in DAG %s", len(dag.tasks))
    for af_task in dag.tasks:
        ti = tis.get(af_task.task_id)
        if ti is None:
            ti = TaskInstance(af_task, execution_date=execution_date)
            ti.start_date = timezone.utcnow()
            ti.end_date = timezone.utcnow()

            logger.debug(
                "create dagrun - task instance create %s -> %s",
                af_task.task_id,
                ti.state,
            )
            session.add(ti)

        logger.debug(
            "create dagrun - task instance %s -> %s", af_task.task_id, ti.state
        )
        task_run = databand_run.get_task_run_by_af_id(af_task.task_id)
        # all tasks part of the backfill are scheduled to dagrun

        # Set log file path to expected airflow log file path
        task_run.task_run_executor.log_manager.local_log_file.path = (
            compute_log_filepath_from_ti(ti, execution_date)
        )
        if task_run.is_reused:
            # this task is completed and we don't need to run it anymore

            logger.debug(
                "create dagrun - task_run is reused on ti create %s -> %s task_run_state",
                af_task.task_id,
                task_run.task_run_state,
            )
            ti.state = State.SUCCESS
            ti.try_number = 1

    session.commit()

    return dagrun


class AirflowTaskExecutor(RunExecutorEngine):
    """
    Bridge to Airflow Execution
    """

    def __init__(
        self, run_executor, task_executor_type, host_engine, target_engine, task_runs
    ):
        super(AirflowTaskExecutor, self).__init__(
            run_executor=run_executor,
            task_executor_type=task_executor_type,
            host_engine=host_engine,
            target_engine=target_engine,
            task_runs=task_runs,
        )

        self.airflow_config = AirflowConfig()
        self.airflow_task_executor = self._get_airflow_executor()

        self._validate_airflow_db()

        self.dag: typing.Optional[DAG] = None
        self.dag_run: typing.Optional[DagRun] = None

        # caching for Optimized Rule in airflow
        self._ti_state_manager = AirflowTaskInstanceStateManager()

        self._runtime_k8s_zombie_cleaner = None

    def get_ti_state_manager(self):
        return self._ti_state_manager

    def _validate_airflow_db(self):
        from airflow import configuration, settings

        # getting url directly from airflow
        # it's possible that
        #  * user use _cmd to generate url ( we don't want to have an extra call there)
        #  * Session was initialized with different value than AIRFLOW__CORE__SQL_CONN_STRING
        conn_string_url = settings.Session.session_factory.kw["bind"].url

        logger.info(
            "Using airflow executor '%s' with airflow DB at '%s' \nAIRFLOW_HOME='%s'",
            self.airflow_task_executor.__class__.__name__,
            conn_string_url.__repr__(),
            configuration.AIRFLOW_HOME,
        )

        not_exist_help_msg = (
            "Check that sql_alchemy_conn in airflow.cfg or environment variable "
            + "SQL_ALCHEMY_CONN is set correctly."
        )
        not_initialised_help_mdg = "Make sure that you run the command: airflow initdb"

        err_msg = (
            "You are running in Airflow mode (run_executor={}) with DB at {}".format(
                self.run_executor.run_config.task_executor_type,
                conn_string_url.__repr__(),
            )
        )

        from dbnd_run._vendor.database import database_exists

        try:
            database_exists(conn_string_url)
        except Exception as ex:
            raise DatabandError(
                "Airflow DB is not found! %s : %s" % (err_msg, str(ex)),
                help_msg=not_exist_help_msg,
                nested_exceptions=[],
            )

        try:
            with create_session() as session:
                session.query(DagRun).first()
        except Exception as ex:
            raise DatabandError(
                "Airflow DB is not initialized! %s : %s" % (err_msg, str(ex)),
                help_msg=not_initialised_help_mdg,
            )

        pool_help_msg = (
            "Check that you did not change dbnd_pool configuration in airflow.cfg "
            + "and that you run the command: airflow initdb."
        )

        user_defined_pool = dbnd_config.get("airflow", "dbnd_pool")
        is_defined_pool_dbnd = user_defined_pool == "dbnd_pool"
        is_user_pool_in_db = (
            session.query(Pool.pool).filter(Pool.pool == user_defined_pool).first()
            is not None
        )

        if not is_user_pool_in_db:
            if is_defined_pool_dbnd:
                create_airflow_pool(user_defined_pool)
            else:
                raise DatabandError(
                    "Airflow DB does not have dbnd_pool entry in slots table",
                    help_msg=pool_help_msg,
                )

    def build_airflow_dag(self, task_runs):
        # create new dag from current tasks and tasks selected to run
        root_task = self.run.root_task_run.task
        if isinstance(root_task, AirflowDagAsDbndTask):
            # it's the dag without the task itself
            dag = root_task.dag
            set_af_doc_md(self.run, dag)
            for af_task in dag.tasks:
                task_run = self.run.get_task_run(operator_to_to_dbnd_task_id(af_task))
                set_af_operator_doc_md(task_run, af_task)
            return root_task.dag

        # paused is just for better clarity in the airflow ui
        dag = DAG(
            self.run.dag_id,
            default_args=get_dbnd_default_args(),
            is_paused_upon_creation=True,
            concurrency=self.airflow_config.dbnd_dag_concurrency,
        )
        if hasattr(dag, "_description"):
            dag._description = "Dynamic DAG generated by DBND"

        with dag:
            airflow_ops = {}
            for task_run in task_runs:
                task = task_run.task
                if isinstance(task, AirflowOperatorAsDbndTask):
                    op = task.airflow_op
                    # this is hack, we clean the state of the op.
                    # better : implement proxy object like
                    # databandOperator that can wrap real Operator
                    op._dag = dag
                    op.upstream_task_ids.clear()
                    if AIRFLOW_VERSION_AFTER_2_2:
                        op.task_group = dag.task_group
                        dag.task_group.add(op)
                    dag.add_task(op)
                    set_af_operator_doc_md(task_run, op)
                else:
                    # we will create DatabandOperator for databand tasks
                    op = build_dbnd_operator_from_taskrun(task_run)

                airflow_ops[task.task_id] = op

            for task_run in task_runs:
                task = task_run.task
                op = airflow_ops[task.task_id]
                upstream_tasks = task.ctrl.task_dag.upstream
                for t in upstream_tasks:
                    if t.task_id not in airflow_ops:
                        # we have some tasks that were not selected to run, we don't add them to graph
                        continue
                    upstream_ops = airflow_ops[t.task_id]
                    if upstream_ops.task_id not in op.upstream_task_ids:
                        op.set_upstream(upstream_ops)

        dag.fileloc = (
            root_task.task_definition.source_code.task_source_file_for_internal_usage
        )
        set_af_doc_md(self.run, dag)
        return dag

    def do_run(self):
        self._fix_db_listener()

        self.dag = dag = self.build_airflow_dag(task_runs=self.task_runs)

        with set_dag_as_current(dag):
            report_airflow_task_instance(
                dag.dag_id, self.run.execution_date, self.task_runs, self.airflow_config
            )
            self.dag_run = self.create_dag_run(dag)
            try:
                self.run_airflow_dag(dag)

            finally:

                if self.dag_run:
                    fix_zombie_dagrun_task_instances(self.dag_run)

    def _pickle_dag_and_save_pickle_id_for_versioned(self, dag, session):
        dp = DagPickle(dag=dag)

        # First step: we need pickle id, so we save none and "reserve" pickle id
        dag.last_pickled = timezone.utcnow()
        dp.pickle = None
        session.add(dp)
        session.commit()

        # Second step: now we have pickle_id , we can add it to Operator config
        # dag_pickle_id used for Versioned Dag via TaskInstance.task_executor <- Operator.task_executor
        dag.pickle_id = dp.id
        for op in dag.tasks:
            if op.executor_config is None:
                op.executor_config = {}
            op.executor_config["DatabandExecutor"] = {
                "dbnd_driver_dump": str(self.run.run_executor.driver_dump),
                "dag_pickle_id": dag.pickle_id,
                "remove_airflow_std_redirect": self.airflow_config.remove_airflow_std_redirect,
            }

        # now we are ready to create real pickle for the dag
        with ready_for_pickle(dag, DAG_UNPICKABLE_PROPERTIES) as pickable_dag:
            dp.pickle = pickable_dag
            session.add(dp)
            session.commit()

        dag.pickle_id = dp.id
        dag.last_pickled = timezone.utcnow()

    def _fix_db_listener(self):
        if not self.airflow_config.disable_db_ping_on_connect:
            return

        from airflow import settings as airflow_settings

        try:
            remove_listener_by_name(
                airflow_settings.engine, "engine_connect", "ping_connection"
            )
        except Exception as ex:
            logger.warning("Failed to optimize DB access: %s" % ex)

    @provide_session
    def create_dag_run(self, dag, session=None):
        af_dag = dag
        databand_run = self.run
        execution_date = databand_run.execution_date
        s_run = self.run_executor.run_config  # type: RunConfig

        run_id = s_run.id
        if not run_id:
            # we need this name, otherwise Airflow will try to manage our local jobs at scheduler
            # ..zombies cleanup and so on
            run_id = "backfill_{0}_{1}".format(
                databand_run.name, databand_run.execution_date.isoformat()
            )

        self._pickle_dag_and_save_pickle_id_for_versioned(af_dag, session=session)
        af_dag.sync_to_db(session=session)
        logger.info("create_dagrun_from_dbnd_run starts ")
        # let create relevant TaskInstance, so SingleDagRunJob will run them
        dagrun = create_dagrun_from_dbnd_run(
            databand_run=databand_run,
            dag=af_dag,
            run_id=run_id,
            execution_date=execution_date,
            session=session,
            state=State.RUNNING,
            external_trigger=False,
        )
        return dagrun

    @provide_session
    def run_airflow_dag(self, dag, session=None):
        # type:  (DAG, Session) -> None
        af_dag = dag
        databand_run = self.run
        s_run = self.run_executor.run_config  # type: RunConfig

        if isinstance(self.airflow_task_executor, InProcessExecutor):
            heartrate = 0
        else:
            # we are in parallel mode
            heartrate = airflow_conf.getfloat("scheduler", "JOB_HEARTBEAT_SEC")

        # "Amount of time in seconds to wait when the limit "
        # "on maximum active dag runs (max_active_runs) has "
        # "been reached before trying to execute a dag run "
        # "again.
        delay_on_limit = 1.0

        self.airflow_task_executor.fail_fast = s_run.fail_fast
        # we don't want to be stopped by zombie jobs/tasks
        if AIRFLOW_VERSION_2:
            airflow_conf.set("core", "max_active_tasks_per_dag", str(10000))

            dbnd_task_runner = (
                "dbnd_run.airflow.compat.dbnd_task_runner.DbndStandardTaskRunner"
            )

            # workaround for --pickle and --dag in the same command line
            # we pickle our dags, while standard airflow is not doing that anymore
            # some code paths are broken, this is a workaround to remove
            # pickle_id from the command line of "--raw", as this will run via .fork,
            # while dag object is loaded already from DB

            # fix value in the current process
            from airflow.task import task_runner as airflow_task_runner_module

            airflow_task_runner_module._TASK_RUNNER_NAME = dbnd_task_runner

            # bypass new value to spawned processes
            os.environ["AIRFLOW__CORE__TASK_RUNNER"] = dbnd_task_runner

            # consistent config, but there is no side-affect of this statement
            airflow_conf.set("core", "task_runner", dbnd_task_runner)
        else:
            airflow_conf.set("core", "dag_concurrency", str(10000))

        airflow_conf.set("core", "max_active_runs_per_dag", str(10000))
        donot_pickle = s_run.donot_pickle or airflow_conf.getboolean(
            "core", "donot_pickle"
        )

        if (
            self.airflow_config.clean_zombie_task_instances
            and "KubernetesExecutor" in self.airflow_task_executor.__class__.__name__
        ):
            from dbnd_run.airflow.executors.kubernetes_executor.kubernetes_runtime_zombies_cleaner import (
                ClearKubernetesRuntimeZombiesForDagRun,
            )

            self._runtime_k8s_zombie_cleaner = ClearKubernetesRuntimeZombiesForDagRun(
                k8s_executor=self.airflow_task_executor
            )
            logger.info(
                "Zombie cleaner is enabled. "
                "It runs every %s seconds, threshold is %s seconds",
                self._runtime_k8s_zombie_cleaner.zombie_query_interval_secs,
                self._runtime_k8s_zombie_cleaner.zombie_threshold_secs,
            )

        if self.airflow_config.use_legacy_single_dag_run_job or AIRFLOW_VERSION_1:
            from dbnd_run.airflow.scheduler.af1_single_dag_run_job import (
                SingleDagRunJob,
            )

            self.backfill_job = SingleDagRunJob(
                dag=af_dag,
                execution_date=databand_run.execution_date,
                mark_success=s_run.mark_success,
                executor=self.airflow_task_executor,
                donot_pickle=donot_pickle,
                ignore_first_depends_on_past=s_run.ignore_first_depends_on_past,
                ignore_task_deps=s_run.ignore_dependencies,
                fail_fast=s_run.fail_fast,
                pool=s_run.pool,
                delay_on_limit_secs=delay_on_limit,
                verbose=is_verbose(),
                heartrate=heartrate,
                airflow_config=self.airflow_config,
            )
            self.backfill_job._log = PrefixLoggerAdapter(
                "scheduler", self.backfill_job.log
            )

            self.backfill_job.run()

        else:
            if not AIRFLOW_VERSION_2:
                raise Exception(
                    "Please change dbnd configuration to airflow.use_legacy_single_dag_run_job=True"
                )
            from dbnd_run.airflow.scheduler.af2_single_dag_run_job import (
                SingleDagRunJob,
            )

            self.backfill_job = SingleDagRunJob(
                dag=af_dag,
                start_date=databand_run.execution_date,
                end_date=databand_run.execution_date,
                mark_success=s_run.mark_success,
                executor=self.airflow_task_executor,
                ignore_first_depends_on_past=s_run.ignore_first_depends_on_past,
                ignore_task_deps=s_run.ignore_dependencies,
                continue_on_failures=not s_run.fail_fast,
                pool=s_run.pool,
                delay_on_limit_secs=delay_on_limit,
                verbose=is_verbose(),
                run_at_least_once=True,  # important for one time execution!
                donot_pickle=True,  # already pickled by us
                heartrate=heartrate,
            )

            self.backfill_job.run()

    def _get_airflow_executor(self):
        """Creates a new instance of the configured executor if none exists and returns it"""
        if self.task_executor_type == AirflowTaskExecutorType.airflow_inprocess:
            return InProcessExecutor()

        if (
            self.task_executor_type
            == AirflowTaskExecutorType.airflow_multiprocess_local
        ):
            if self.run_executor.run_config.parallel:
                return LocalExecutor()
            else:
                return SequentialExecutor()

        if self.task_executor_type == AirflowTaskExecutorType.airflow_kubernetes:
            assert_plugin_enabled("dbnd-docker")

            from dbnd_docker.kubernetes.kubernetes_engine_config import (
                KubernetesEngineConfig,
            )
            from dbnd_run.airflow.executors.kubernetes_executor.kubernetes_executor import (
                DbndKubernetesExecutor,
            )

            if not isinstance(self.target_engine, KubernetesEngineConfig):
                raise errors.executor_k8s.kubernetes_with_non_compatible_engine(
                    self.target_engine
                )
            if self.target_engine.debug:
                logging.getLogger("airflow.contrib.kubernetes").setLevel(logging.DEBUG)

            return DbndKubernetesExecutor(kubernetes_engine_config=self.target_engine)

    def clean_zombie_dagruns_if_required(self):
        if self.airflow_config.clean_zombies_during_backfill:
            from dbnd_run.airflow.scheduler.dagrun_zombies_clean_job import (
                DagRunZombiesCleanerJob,
            )

            DagRunZombiesCleanerJob().run()

    def handle_process_dag_task_instanced_iteration(self, ti_status):
        all_ti = list(ti_status.to_run.values())
        if self.dag_run:
            self._ti_state_manager.refresh_task_instances_state(
                all_ti, self.backfill_job.dag.dag_id, self.dag_run.execution_date
            )
            airflow_to_databand_sync.update_databand_task_run_states(self.dag_run)
            airflow_to_databand_sync.sync_task_run_attempts_retries(ti_status)

            if self._runtime_k8s_zombie_cleaner:
                # this code exists in airflow original scheduler
                # clean zombies ( we don't need multiple runs here actually
                self._runtime_k8s_zombie_cleaner.find_and_clean_dag_zombies(
                    dag=self.dag, execution_date=self.dag_run.execution_date
                )

        if is_killed():
            raise errors.task_execution.databand_context_killed(
                "SingleDagRunJob scheduling main loop"
            )


def set_af_doc_md(run, dag):
    dag.doc_md = (
        "### Databand Info\n"
        "* **Tracker**: [{0}]({0})\n"
        "* **Run Name**: {1}\n"
        "* **Run UID**: {2}\n".format(run.run_url, run.name, run.run_uid)
    )


@contextlib.contextmanager
def set_dag_as_current(dag):
    """
    replace current dag of the task with the current one
    operator can have different dag if we rerun task
    :param dag:
    :return:
    """
    task_original_dag = {}
    try:
        # money time  : we are running dag. let fix all tasks dags
        # in case tasks didn't have a proper dag
        for af_task in dag.tasks:
            task_original_dag[af_task.task_id] = af_task.dag
            af_task._dag = dag
        yield dag
    finally:
        for af_task in dag.tasks:
            original_dag = task_original_dag.get(af_task.task_id)
            if original_dag:
                af_task._dag = original_dag
