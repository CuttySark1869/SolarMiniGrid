# apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime


def schedule_opt():
    print(datetime.now().strftime("%Y-%M-%d %H:%M:%S"))


scheduler=BackgroundScheduler()
scheduler.add_job(schedule_opt,'cron', second=30)
scheduler.start()