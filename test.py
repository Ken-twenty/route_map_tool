class A():

    def __init__(self):
        self.name = "origin"

class B(A):

    def sayHi(self):
        print(self.name)

b = B()
b.sayHi()