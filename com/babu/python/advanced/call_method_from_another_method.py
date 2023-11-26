class MyClass:
  def __init__(self):
      self.name="babu"
      self.final_name="1"
  def add_first_name(self):
      return self.name+" gali"

  def add_last_name(self):
      self.final_name = self.add_first_name();

obj = MyClass()
obj.add_first_name()
print(obj.add_first_name())


