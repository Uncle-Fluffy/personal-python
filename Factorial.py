print "hello Universe"

class Factorial(object):
    def __init__(self, n):
        self.n = n

    def fact(self):
        if n > 1:
            return n * self.fact(self.n-1)
        else:
            return 1

    def show(self):
        print (self.n)

    def hello(self):
        print ("Hello World")
        

x1 = Factorial(4)
x1.hello(4)

