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
