from mosamatic2.core.tasks.task import Task


class Pipeline(Task):
    def __init__(self, inputs, params, output, overwrite=False):
        super(Pipeline, self).__init__(inputs, params, output, overwrite)
        self._tasks = []

    def add_task(self, task):
        self._tasks.append(task)

    def run(self):
        for task in self._tasks:
            task.run()