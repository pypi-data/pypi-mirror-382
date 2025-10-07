# © Copyright Databand.ai, an IBM Company 2022

import abc

from dbnd._core.constants import TaskType
from dbnd_run.current import try_get_run_executor
from dbnd_run.task.task import Task


class PipelineTask(Task):
    """
    Use for tasks that only wrap other tasks and that by definition are done if all their requirements exist.

    Example::

        class PrepareData(PipelineTask):
            data = parameter.data
            prepared_data = output.csv.data

            def band(self):
                self.prepared_data = gather_data.dbnd_run()
    """

    _conf__task_type_name = TaskType.pipeline

    def _task_run(self):
        """We override, as we don't want to automatically load deferred inputs as we do it in regular task."""
        result = self.run()
        return result

    @abc.abstractmethod
    def band(self):
        """
        This is the method you should override while using PipelineTask.

        we need to implement result of this function to be "output" of the task (task_output, and vars)
        Your Pipeline.band() call should have one or more tasks wired one into another.
        See examples!"
        """
        return

    def _complete(self):
        if self.task_band:
            if not self.task_band.exists():
                return False
            # With very large pipelines, checking all tasks might take a very long time
            # so we might want to assume that if the band exist, probably all outputs also exist
            re = try_get_run_executor()
            if re and re.run_config.pipeline_band_only_check:
                return True
        return super(PipelineTask, self)._complete()


PipelineTask.task_definition.hidden = True
