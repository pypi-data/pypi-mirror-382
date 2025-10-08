import datetime

from fans.jober import Jober


def func():
    print(datetime.datetime.now())


jober = Jober(capture=False)
jober.add_job(func, sched=1)
jober.wait()
