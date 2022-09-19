# MIT License
#
# Copyright (c) 2022 Mariusz Okulanis
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__version__ = '1.0.0'

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
