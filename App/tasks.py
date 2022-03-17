from email import header
from celery import Celery, chain, group, chord
from celery.schedules import crontab

app = Celery(broker='pyamqp://guest@localhost//',)

app.conf.update(
    task_serializer='pickle',
    result_serializer='pickle',
    accept_content=['pickle']
)

# Função agendadas

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # Executa a cada 30 s
    sender.add_periodic_task(30, hello.s())

    # Executa todos os dias as 8:00
    sender.add_periodic_task(crontab(hour=8, minute=0), funcao_1.s())

    # Executa todas as manhãs de segunda-feira as 8:00
    sender.add_periodic_task(crontab(hour=8, minute=0, day_of_week=1), funcao_2.s())

    # Executado no segundo dia de cada mês as 8:00
    sender. add_periodic_task(crontab(hour=8, minute=0, day_of_month='2'), funcao_3.s())

@app.task
def hello():
    print('World')

@app.task
def funcao_1():
    pass

@app.task
def funcao_2():
    pass

@app.task
def funcao_3():
    pass


# Trabalhando com funções assincronas

"""
## Chains

Usamos o chain quando queremos que uma função assincrona
receba o resultado de outra função assincrona. A segunda 
task sempre pega o resultado da primeira como o primeiro
argumento.
"""

@app.task
def soma(x, y):
    return x + y

# A segunda função recebe apenas um argumento, isso pq o valor de retorno da
# primeira task vai ser o primeiro argumento da segunda. Mesma coisa que: soma.s(3,3)
resultado = chain(soma.s(1,2), soma.s(3)).apply_async()


"""
## Groups

Groups são usados para executar tarefas em paralelo. A função group
recebe uma lista de assinaturas.
"""

tarefas = group([
    soma.s(2,2), soma.s(4,4)
])

resultado = tarefas.apply_async()

# Para saber se todas as tarefas já estão completas
resultado.ready() # True ou False

# Para saber se todas as tarefas executaram com sucesso
resultado.successful() # True ou False

# Para obter o resultado das tarefas
resultado.get() # [4,8]


"""
## Chords

Chords é uma tarefa que é executada apenas depois de todas as tarefas
no conjunto de tarefas serem finalizadas
"""

@app.task
def soma_geral(numeros):
    return sum(numeros)

# O callback é executado depois que o grupo de tasks foi finalizado
callback = soma_geral.s()

# O Header é um simples grupo de taks
_header = [soma.s(2,2), soma.s(4, 4)]

resultado_chord = chord(_header)(callback)

resultado_chord.get() # 12