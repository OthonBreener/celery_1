# Rodando o projeto

* Iniciando o docker:
    sudo service docker start

* Iniciando o rabbitmq:
    docker run -d -p 5672:5672 rabbitmq

* Iniciando o celery:
    celery -A tasks worker --loglevel=INFO

* Iniciando uma task periodica:
    celery -A tasks worker --beat --loglevel=INFO

* Iniciando o flower:
    celery -A tasks flower --adress=0.0.0.0 --port=5566

## Informações:

* Separe uma aplicação celery em dois arquivos:
  * O primeiro para criar o app celery e definir as tasks
  * O segundo para enviar a função para o broker, utilizando o .delay()

## O decorador @task e suas funcionalidades:

O decorador de task fornece vários mecanismos que nos auxiliam a manter a confiabilidade
da nossa execução e ter um sistema mais disponível.

* bind: @task(bind=True)

Permite que tenhamos acesso ao objeto task que faz o warper da nossa função.
Exemplo:

```python

@app.task(bind=True)
def minha_task(self):
  # Reexecuta a task (para caso de erro)
  self.retry()

  #Diz se foi chamado por outra task
  self.request.called_directly

  # Atualiza o status da task
  self.update_state(state='SUCCES')

  # Contém diversas informações interessantes
  self.request

```

* max_retry
* default_retry_delay
* autoretry_for

Exemplos:

```python

@app.task(
  bind=True,
  max_retry=5, # tentar executar de novo no máximo 5 vezes
  default_retry_delay = 20, #define o tempo entre as tentativas
  autoretry_for=(TypeError,Exception), # Auto retry caso algum erro na tupla aconteça
)

```

* retry_backoff: Defini o tempo no qual o processo vai ser reestartado depois de um erro.
Esse tempo pode ser escolhido como o padrão do celery passando True ou definido pelo usuário.

```python

@app.task(
  retry_backoff=True,
  # ou
  retry_backoff=3,
)
def minha_task(self):
  self.retry()
```

* name: As tasks podem ser nomeadas para serem mais fácil de identifica-las.

```python
@app.task(name="Task 1")
def minha_task(self):
  pass
```

* Execeções no retry:

```python

@app.task(
    name='Texto do documento',
    bind=True,
    retry_backoff=True,
    autoretry_for=(ValueError)
)
def minha_task(user):

    if response.status_code == 200:
      return response.json()

    raise ValueError('Deu erro')


@app.task(bind=True, default_retry_delay=30 * 60)  # retry in 30 minutes.
def add(self, x, y):
    try:
        something_raising()
    except Exception as exc:
        # overrides the default delay to retry after 1 minute
        raise self.retry(exc=exc, countdown=60)

```

## Debug no celery

O celery possui um debugger nativo. Muitas vezes você pode executar a função de maneira simples,
mas problemas acontecem.

```python
from celery.contrib import rdb

@app.task
def task_para_deb():

  rdb.set_trace()
```
Em outro terminal dê o telnet com o url.

## Chain com celery

A ideia do chain é montar pipeline de tasks. O resultado de uma task é o primeiro
parâmetro de outro. Com isso, podemos diminuir a complexidade do nosso código.

```python

from celery import chain

@app.task
def a(x):
    return x*4

@app.task
def b(x,y):
    return x + y

c = chain(a.s(1), b.s(2))
c()

# Nesse caso o b recebe dois parâmetros: o primeiro seria o resultado de a = x,
# e o segundo 2 = y
```

## Executando tasks períodicas

Tarefas podem ser agendadas utilizando o celery beat. O celery usa por padrão o time zone
UTC. Mas você pode definir usando o:

```sh
app.conf.timezone = 'Europe/London'
```
Para chamar uma tarefa periodicamente, você deve adicionar uma entrada à lista de programação
do beat:


```python 

from celery import Celery
from celery.schedules import crontab

app = Celery()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        test.s('Happy Mondays!'),
    )

@app.task
def test(arg):
    print(arg)

@app.task
def add(x, y):
    z = x + y
    print(z)

```