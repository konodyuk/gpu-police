import time
import attr

from box import Box

from gpu_police.config import config
from gpu_police.logging import get_console

@attr.s
class TaskScheduler:
    state = attr.ib(factory=Box)
    tasks = attr.ib(factory=list)
    interval = attr.ib(factory=int)
    console = attr.ib(factory=get_console)
    
    def register(self, *args, **kwargs):
        def inner(task_class):
            if config.general.debug:
                self.console.log(f"Registering {task_class.__name__}")
            self.tasks.append(task_class(*args, **kwargs))
        return inner
    
    def setup(self):
        self.state.interval = self.interval
        
        for task in self.tasks:
            task.setup(self.state)
        
    def run(self):
        self.setup()
        
        iteration = 0
        while True:
            for task in self.tasks:
                if config.general.debug:
                    self.console.log(f"Running {task.__class__.__name__}")
                if (iteration % task.period) > 0:
                    continue
                task(self.state)

            for task in self.tasks:
                if (iteration % task.period) > 0:
                    continue
                task.cleanup(self.state)

            time.sleep(self.interval)
            iteration += 1

ts = TaskScheduler(interval=config.general.interval)
