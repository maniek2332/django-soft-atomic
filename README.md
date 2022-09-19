# django-soft-atomic

A more forgiving variation of `django`'s `atomic`, allowing you to pass some
exceptions through atomic block without rollback.

## Rationale

In big applications you may end up relying on exceptions mechanism to pass information
about failure up the stack. Unfortunately, if your business logic involves operations on
database, there is no easy way to wind up execution through atomic block without
rolling back entire transaction. `django-soft-atomic` tries to solves this problem
by allowing certain exceptions to exit atomic block just like sucessful execution
(still maintaining the raised exception).

## Requirements

 * Python 3.6+
 * Django 3.12+

## Installation

### With PIP

Execute: `pip install django-soft-atomic`

### Manual

Copy `django_soft_atomic.py` to your codebase and simply start using it.

## Usage (docs)

This "package" constists of single function/decorator/context-manager:

`soft_atomic(using=None, savepoint=True, durable=False, *, safe_exceptions=(Exception,))`

 * `using` (default Django parameter) - database name to use,
 * `savepoint` (default Django parameter) - TODO,
 * `durable` (default Django parameter) - TODO,
 * `safe_exceptions` - collection (e.g. `tuple`) of exceptions which are allowed to pass through `soft_atomic` block without rollback. Typical DB errors (like `IntegrityError`) will still throw. Defaults to: `(Exception,)`.

## Example

```
class PaymentProcessingException(Exception):
    pass

class PaymentRequest(models.Model):
    payment_id = models.TextField()
    success = models.BooleanField()

@soft_atomic(safe_exceptions=(PaymentProcessingException,))
def process_payment(payment_details):
    payment_id, success = payment_gateway.process_payment(payment_details)
    PaymentRequest.objects.create(payment_id=payment_id, success=success)
    if not success:
        raise PaymentProcessingException("Payment was not sucessful")

def payment_endpoint(payment_details):
    try:
        process_payment(payment_details)
    except PaymentProcessingException:
        ...  # handle a failure
    else:
        ...  # payment was successful
    # in either case the `PaymentRequest` record was created in the database
```
