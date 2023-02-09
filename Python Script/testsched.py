from apscheduler.schedulers.background import BackgroundScheduler
import time


def my_job_function():
  print('function 1')

def another_job_function():
  print('function 2')


if __name__ == '__main__':
  scheduler = BackgroundScheduler()

  # Add some jobs to the scheduler
  scheduler.add_job(my_job_function, 'interval', seconds=1)
  scheduler.add_job(another_job_function, 'interval', seconds=2)

  # Start the scheduler
  scheduler.start()
  time.sleep(10)