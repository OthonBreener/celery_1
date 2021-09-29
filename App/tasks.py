from celery import Celery
from celery.schedules import crontab

app = Celery(broker='pyamqp://guest@localhost//',)

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(1, ola_mundo.s(), expires=10)

@app.task
def ola_mundo():
    return "Olá mundo"

@app.task
def hellow_world():
    return "Hey there!"
