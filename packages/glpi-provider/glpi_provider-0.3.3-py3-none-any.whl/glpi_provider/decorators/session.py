from functools import wraps



def with_session(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self.service.create_session()  # Cria a sessão antes de chamar o método
        try:
            return func(self, *args, **kwargs)
        finally:
            self.service.close_session()  # Garante que a sessão será fechada após a execução
    return wrapper