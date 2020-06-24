import os
from abc import ABC, abstractmethod
from collections import defaultdict

import attr
from box import Box

from gpu_police.scheduler import ts
from gpu_police.config import config
from gpu_police.sheets_middleware import get_whitelist
from gpu_police.process import Process
from gpu_police.logging import get_console

class Task(ABC):
    period = 1
    
    def __call__(self, state):
        try:
            self.run(state)
        except:  # may also handle it with rich logger
            self.setup(state)
            self.run(state)
    
    def setup(self, state):
        pass
    
    @abstractmethod
    def run(self, state):
        pass
        
    def cleanup(self, state):
        pass


@ts.register()
class FetchProcesses(Task):
    """adds current processes to window"""

    def run(self, state):
        running_processes = self.fetch()
        state.running_processes = running_processes
        state.window.append(running_processes)
    
    @staticmethod
    def fetch():
        res = list(map(Process.from_str, os.popen('nvidia-smi pmon -c 1 -s um').read().strip().split('\n')[2:]))
        return [i for i in res if not i.is_special]


@ts.register(window_size=config.general.window_size)
@attr.s
class CutWindow(Task):
    """keeps window of a certain size"""

    window_size = attr.ib(default=1)
    
    def setup(self, state):
        state.window = []
        state.window_size = self.window_size
        
    def run(self, state):
        state.window = state.window[-self.window_size:]
        

@ts.register()
class ComputeStats(Task):
    """computes whether each process was active during the last window_size iters"""

    def run(self, state):
        stats = defaultdict(Box)
        for process in state.running_processes:
            stats[process].idle = True
            
            if len(state.window) < state.window_size:
                stats[process].idle = False
                continue
            
            for snapshot in state.window:
                process_hist = self._find_in_snapshot(process, snapshot)
                if (process_hist is None) or process_hist.is_active:
                    stats[process].idle = False
                    break

        state.stats = stats

    @staticmethod
    def _find_in_snapshot(process, snapshot):
        for item in snapshot:
            if item == process:
                return item
        return None


@ts.register(period=config.whitelist.period)
@attr.s
class UpdateWhitelist(Task):
    """updates whitelist, runs each `period` iterations"""
    
    period = attr.ib(default=10)
    
    def run(self, state):
        state.whitelist = get_whitelist()


@ts.register()
class KillBlacklisted(Task):
    """kills processes whose users are not in whitelist"""

    def setup(self, state):
        state.killed = []
        
    def run(self, state):
        for process in state.running_processes:
            if process.user not in state.whitelist:
                if not config.general.debug:
                    process.kill()
                state.killed.append({
                    'process': process, 
                    'reason': 'not in whitelist'
                })


@ts.register(memory_threshold=400)
@attr.s
class KillIdle(Task):
    """kills idle processes"""

    memory_threshold = attr.ib(default=0)
    
    def setup(self, state):
        state.killed = []

    def run(self, state):
        for process in state.running_processes:
            if state.stats[process].idle and process.memory_consumption > self.memory_threshold:
                if not config.general.debug:
                    process.kill()
                state.killed.append({
                    'process': process, 
                    'reason': f'inactive for {state.window_size * state.interval}s, '
                              f'memory consumption: {process.memory_consumption}MB > {self.memory_threshold}MB (idle threshold)'
                })


@ts.register()
class Log(Task):
    def __init__(self):
        outfile = open(config.log.file, "a")
        self.console = get_console(outfile)
    
    def run(self, state):
        for item in state.killed:
            self.log(f"Killed: {item['process']}\nReason: {item['reason']}")
        state.killed.clear()
            
    def log(self, line):
        self.console.log(line, end='\n\n')
