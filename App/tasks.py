from celery import Celery
from celery.schedules import crontab
from celery.exceptions import SoftTimeLimitExceeded
from json import load, dump
from celery.contrib import rdb
from datetime import datetime

app = Celery(broker='pyamqp://guest@localhost//',)

app.conf.update(
    task_serializer='pickle',
    result_serializer='pickle',
    accept_content=['pickle']
)

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(10, hellow_world.s(sender))

@app.task(bind=True)
def ola_mundo(self, var):
    print('Executing task id {0.id}'.format(self.request))

    if var.get('controlador') != 'tocando':
        return "Não enviado"

    with open('../teste1.json', 'w') as tt:
        var.update({'task_id': self.request.id})
        #var.update({'time': 'entrei aqui no ola_mundo'})
        dump(var, tt)


    return "Olá mundo"

@app.task
@app.on_after_configure.connect
def hellow_world(sender, **kwargs):

    #rdb.set_trace()

    with open('../teste1.json') as tt:
        var = load(tt)

    if var.get('chave') == 'not_selection_botton' and not var.get('task_id'):
        print("Entrei no if")

        sender.add_periodic_task(10, ola_mundo.s(var))
