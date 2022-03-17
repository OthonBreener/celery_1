from datetime import datetime, timedelta

# formatando o objeto de data
data = datetime(2021,10,4)
print(data)
print(data.strftime('%d/%m/%Y'))

# criando um objeto de data apartir de uma string
data_r = '4/10/2021'
n_data = datetime.strptime(data_r, '%d/%m/%Y')
print(n_data)

# timestamp é a data em segundos
print(n_data.timestamp())

# é possível converter o timestamp para data normal
stamp = 1633316400.0
data_st = datetime.fromtimestamp(stamp)
print(data_st)

# somando dias a uma data
new_data = data_st + timedelta(days = 5)
print(new_data)

# subtraindo datas
data1 = datetime(2021,10,4)
data2 = datetime(2021,10,10)
dfi = data2 - data1
print(dfi.days)

# datas podem ser comparadas com: == (igual), > (maior), < (menor)
