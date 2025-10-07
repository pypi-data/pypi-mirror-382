from access_specifiers import api as access_specifiers

def enforce_with(cls):
    class Protector(access_specifiers.Restricted):
        def __init__(self):
            self.authorize(WithEnforced)
            
        def get_hidden_cls(self):
            hidden_cls = self.get_hidden_value(cls)
            return hidden_cls
        
    class WithEnforced(access_specifiers.Restricted):
        def __init__(self, *args, **kwargs):
            private = self.private
            private ._obj = hidden_cls.value(*args, **kwargs)
            
        def __enter__(self):
            return self._obj.__enter__()

        def __exit__(self, exc_type, exc_value, traceback):
            return self._obj.__exit__(exc_type, exc_value, traceback)

        def __aenter__(self):
            return self._obj.__aenter__()

        def __aexit__(self, exc_type, exc_value, traceback):
            return self._obj.__aexit__(exc_type, exc_value, traceback)

        def __getattr__(self, name):
            raise AttributeError("This is just a wrapper object. Enter the context manager (i.e, by using a with statement) to access the actual object.")

        def __setattr__(self, name, value):
            raise AttributeError("This is just a wrapper object. Enter the context manager (i.e, by using a with statement) to access the actual object.")        

        def __delattr__(self, name, value):
            raise AttributeError("This is just a wrapper object. Enter the context manager (i.e, by using a with statement) to access the actual object.")        

    protector = Protector()
    hidden_cls = protector.get_hidden_cls()
    return WithEnforced


