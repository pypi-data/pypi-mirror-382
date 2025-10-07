import enforce_with

@enforce_with.enforce_with
class MyClass:
    def __init__(self):
        print("initializing")
        
    def __enter__(self):
        print("entering")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("exiting")

with MyClass() as obj:
    pass

