from apscheduler.schedulers.blocking import BlockingScheduler

from vaccine import check_for_appointments

sched = BlockingScheduler()
print("starting")

# Ideally we would have one process schedule the jobs
# and another process run the jobs, but this is fine for now.
@sched.scheduled_job("interval", seconds=2)
def timed_job():
    check_for_appointments()


sched.start()
