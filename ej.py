from operator import attrgetter


class Objeto():
    def __init__(self,valor):
        self.valor = valor

array = []

array.append(Objeto(3))
array.append(Objeto(10))
array.append(Objeto(4))
array.append(Objeto(2))
array.append(Objeto(9))

for i in array:
    print(i.valor)

print("______")

ancestor = min(array, key=attrgetter('valor'))
array.remove(ancestor)

for i in array:
    print(i.valor)
