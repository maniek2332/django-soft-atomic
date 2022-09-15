import django.db.transaction


class SoftAtomic(django.db.transaction.Atomic):
    """
    Context manager built on top of original atomic.

    It's purpose is to allow certain exceptions other that db-integrity errors
    (e.g. when exception is "expected" and results still should be saved
    to database.)
    """

    # list of exceptions which should handled as standard Atomic would do
    # (execute rollback)
    FATAL_EXCEPTIONS = (django.db.Error,)

    def __init__(self, using, savepoint, durable, safe_exceptions):
        self.safe_exceptions = safe_exceptions
        super().__init__(using, savepoint, durable)

    def __exit__(self, exc_type, exc_value, traceback):
        if (
                exc_type
                and not issubclass(exc_type, self.FATAL_EXCEPTIONS)
                and issubclass(exc_type, self.safe_exceptions)
        ):
            super(SoftAtomic, self).__exit__(None, None, None)
        else:
            super(SoftAtomic, self).__exit__(exc_type, exc_value, traceback)


def soft_atomic(using=None, savepoint=True, durable=False, *, safe_exceptions=(Exception,)):
    if callable(using):
        return SoftAtomic(django.db.transaction.DEFAULT_DB_ALIAS, savepoint, durable, safe_exceptions)(using)
    return SoftAtomic(using, savepoint, durable, safe_exceptions)
