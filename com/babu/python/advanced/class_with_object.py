class Addition:
  def __init__(self, a, b):
    self.a = a
    self.b = b
  def add(self):
    self.c= self.a+self.b
    print(self.c)

obj = Addition(2,3)
del obj.a
print(obj.a)