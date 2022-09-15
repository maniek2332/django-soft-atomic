# django-soft-atomic

A more forgiving variation of `django`'s `atomic`, allowing you to pass some
exceptions through atomic block without rollback.

## Rationale

In big applications you may end up relying on exceptions mechanism to pass information
about failure up the stack. Unfortunately, if your business logic involves operations on
database, there is no easy way to wind up an exception through atomic block without
rolling back entire transaction. `django-soft-atomic` tries to solves this problem
by allowing certain exceptions to exit atomic block just like sucessful execution
(still maintaining the raised exception).

## Installation

```
pip install django-soft-atomic
```

## Requirements

 * Python 3.5+
 * Django 2.12+

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
