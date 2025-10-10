import time
import threading
from typing import List
from dataclasses import dataclass
from ..notifications import send

@dataclass
class MemoryUsage:
    percent: int
    rss: int
    swap:int
    total:int

@dataclass
class MemWatchAlert:
    direction: int   # -1 = down, 1 = up
    percent: int     # percent of memory usage to trigger
    triggered: bool  # was this alert already triggered
    check_interval: float  # seconds to wait before next check
    notification_name: int   # logging level to use

class MemWatch:
    lock: threading.Lock = threading.Lock()
    running: bool = True
    stop_requested:bool = False
    thread: threading.Thread = None
    limits: List[MemWatchAlert] = []
    hist_max: int = 0

    @staticmethod
    def is_running():
        with MemWatch.lock:
            return MemWatch.running
        
    @staticmethod
    def is_stop_requested():
        with MemWatch.lock:
            return MemWatch.stop_requested
        
    @staticmethod
    def clear_trigger_above(percent: int):
        with MemWatch.lock:
            for rep in MemWatch.limits:
                if rep.direction==1 and rep.percent>=percent:
                    rep.triggered = False

    @staticmethod
    def find_trigger(previous_value, current_value):
        alert_up = None
        alert_down = None
        with MemWatch.lock:
            for rep in MemWatch.limits:
                if previous_value < current_value:
                    if rep.direction==1 and previous_value < rep.percent and current_value >= rep.percent and not rep.triggered:
                        alert_up = rep
                        break
                elif current_value < previous_value:
                    if rep.direction ==-1 and previous_value >= rep.percent and current_value < rep.percent:
                        alert_down = rep
        return alert_up, alert_down


# See:
#   https://stackoverflow.com/questions/46212787/how-to-correctly-report-available-ram-within-a-docker-container
#   https://fabiokung.com/2014/03/13/memory-inside-linux-containers/
#   https://serverfault.com/questions/680963/lxc-container-shows-hosts-full-ram-amount-and-cpu-count
def get_memory_usage() -> MemoryUsage:
    with open('/sys/fs/cgroup/memory/memory.stat', 'r') as oo:
        rss = 1
        swap = 1
        total = 1
        all_ = {}
        for a in oo:
            pa = a.split(' ')
            all_[pa[0]] = int(pa[1])
            if pa[0] == 'rss':
                rss = int(pa[1])
            elif pa[0] == 'hierarchical_memsw_limit':
                total = int(pa[1])
            elif pa[0] == 'swap':
                swap = int(pa[1])
        perc = int((rss + swap) / total * 100)
        MemWatch.hist_max = max(MemWatch.hist_max, rss + swap)
    return MemoryUsage(perc, rss, swap, total)

def hist_memory_max(unit='MB') -> str:
    if unit is None:
        unit = 'mb'
    unit=unit.lower()
    if unit == 'b':
        return '{} B'.format(MemWatch.hist_max)
    elif unit == 'kb':
        return '{} KB'.format(int(MemWatch.hist_max / 1024))
    elif unit == 'gb':
        return '{} GB'.format((MemWatch.hist_max / (1024 * 1024 * 1024)))
    else:
        return '{} MB'.format(int(MemWatch.hist_max / (1024 * 1024)))

def _mem_report(notification_name:str, message:str):
    """
    We are logging memory warning message to all currently running
    threads, so every correlationId gets its own message
    """
    send(notification_name, message)

def add_threshold(direction: int, percent: int, check_interval: float, notification_name: int):
    with MemWatch.lock:
        MemWatch.limits.append(MemWatchAlert(direction, percent, False, check_interval, notification_name))
        MemWatch.limits.sort(key=lambda x: (x.direction, x.percent))

def _memory_watch_procedure(wait_before_start=30):
    lap = 4
    previous_usage_perc = 0

    # wait, do not consume resources during service starting
    time.sleep(wait_before_start)

    while not MemWatch.is_stop_requested():
        time.sleep(lap)
        mu = get_memory_usage()
        current_usage_perc = mu.percent
        reported_dec = 101
        alert_up, alert_down = MemWatch.find_trigger(previous_usage_perc, current_usage_perc)
        if alert_up:
                alert_up.triggered = True
                _mem_report(alert_up.notification_name, f'Memory consumption rised above {alert_up.percent}%')
                lap = alert_up.check_interval
        if alert_down:
            if alert_down.percent > reported_dec:
                _mem_report(alert_down.notification_name, f'Memory consumption decreased below {alert_down.percent}%')
                lap = alert_down.check_interval
            reported_dec = alert_down.percent
            MemWatch.clear_trigger_above(alert_down.percent)

        previous_usage_perc = current_usage_perc
        # Here we have information about total memory usage
        #logger.info(f'Mem usage: {m}%')
        #print(f'Mem usage: {m}%')

    with MemWatch.lock:
        MemWatch.running = False
        
    # we got here only if memory watching was stopped
    #print('-stop-')

def _test_mem_consume():
    """
    Test function: this consumes large amount of memory over time
    """
    p = []
    for b in range(2):
        for a in range(20):
            # allocate 400 MBytes per iteration
            p.append(f' {b}{a}3-1234567890-abcd' * 20000000)
            time.sleep(1.5)
        time.sleep(5)
        p = []

def start_memory_watch(wait_before_start=30):
    with MemWatch.lock:
        if MemWatch.thread is None or not MemWatch.thread.is_alive():
            MemWatch.thread = threading.Thread(target=_memory_watch_procedure, args=(wait_before_start,))
            MemWatch.thread.start()
            MemWatch.running = True

def stop_memory_watch():
    with MemWatch.lock:
        if not MemWatch.running:
            return
        MemWatch.stop_requested = True

    while MemWatch.is_running():
        time.sleep(1)

    with MemWatch.lock:
        MemWatch.thread = None
        MemWatch.stop_requested = False    

__all__ = ['start_memory_watch', 'stop_memory_watch', 'add_threshold', 'get_memory_usage', 'hist_memory_max', MemoryUsage]

if __name__=='__main__':
    # testing 
    add_threshold(-1, 80, False, 4, "memorywatch-info")
    add_threshold(-1, 90, False, 2, "memorywatch-warning")
    add_threshold(-1, 95, False, 1, "memorywatch-warning")
    add_threshold(1, 80, False, 2, "memorywatch-warning")
    add_threshold(1, 90, False, 1, "memorywatch-warning")
    add_threshold(1, 93, False, 1, "memorywatch-warning")
    add_threshold(1, 95, False, 1, "memorywatch-critical")
    add_threshold(1, 97, False, 0.5, "memorywatch-critical")
    add_threshold(1, 98, False, 0.5, "memorywatch-critical")
    add_threshold(1, 99, False, 0.5, "memorywatch-critical")


    start_memory_watch(0.1)

    _test_mem_consume()

    stop_memory_watch()
