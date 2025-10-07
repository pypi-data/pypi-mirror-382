# © Copyright Databand.ai, an IBM Company 2022

from collections import Counter, defaultdict
from typing import List

from airflow.models import TaskInstance
from airflow.utils.db import provide_session


class AirflowTaskInstanceStateManager(object):
    """
    AirflowTaskInstanceStateManager holds latest state info for all relevant task_instances
    """

    def __init__(self):
        self.status = defaultdict(dict)

    def _get_dag_run(self, dag_id, execution_date):
        return self.status[(dag_id, execution_date)]

    def refresh_from_db(self, dag_id, execution_date, session):
        TI = TaskInstance
        updated_status = (
            session.query(TI.task_id, TI.state)
            .filter(TI.dag_id == dag_id, TI.execution_date == execution_date)
            .all()
        )

        self.status[(dag_id, execution_date)] = dict(updated_status)

    def get_state(self, dag_id, execution_date, task_id):
        return self._get_dag_run(dag_id, execution_date).get(task_id)

    def get_aggregated_state_status(self, dag_id, execution_date, task_ids):
        status = self._get_dag_run(dag_id, execution_date)
        return Counter(status.get(task_id) for task_id in task_ids)

    def sync_to_object(self, task_instances):
        # type: (List[TaskInstance]) ->None

        for ti in task_instances:
            ti.state = self.get_state(ti.dag_id, ti.execution_date, ti.task_id)

    @provide_session
    def refresh_task_instances_state(
        self, task_instances, dag_id, execution_date, session=None
    ):
        self.refresh_from_db(dag_id, execution_date, session)
        self.sync_to_object(task_instances)
