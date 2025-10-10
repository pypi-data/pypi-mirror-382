# dcnr-spring

Minimal example package. After installation:

```python

from dcnr_scheduler import scheduled, ScheduledPlan
from datetime import datetime

@scheduled("at * on mon-fri freq 30/hour")
def print_msg(plan:ScheduledPlan, curr_dt:datetime):
    print(curr_dt, 'Hello world')

```

Internal engine of scheduler checks every 60 seconds by default the 
aligibility of functions to execute. That poses a limitation for maximum
frequency of 60 executions per hour. To increase the limit, you can set the period
of internal scheduler checks.

```python
from dcnr_scheduler import ScheduledPlan

ScheduledPlan.set_period(30)
```

Argument of `set_period` is number of seconds (integer)

