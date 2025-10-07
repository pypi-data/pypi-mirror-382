# enforce-with
This library makes it possible to enforce the usage of ```with``` keyword

# Installation
```pip install enforce-with```

# Usage
@enforce_with.**enforce_with**

Decorate your class with this decorator and it will no longer be possible to access the members of its instances unless you access them inside a ```with``` block. Example:
```python
@enforce_with.enforce_with
class MyClass:
    def __init__(self):
        self.var = 10

    def func(self):
        pass

    def __enter__(self):
        print("entering")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("exiting")

with MyClass() as obj:
    obj.var # Ok
    obj.func() # Ok

MyClass().var # Error
MyClass().func() # Error

```
