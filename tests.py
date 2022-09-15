from decimal import Decimal

import django.db
import pytest

from django_soft_atomic import soft_atomic
from test_project.payments.models import PaymentRequest


class PaymentProcessingException(Exception):
    pass


def _process_payment(amount):
    if amount < Decimal("0.00"):
        raise ValueError("Invalid amount")
    elif amount > Decimal("100.00"):
        PaymentRequest.objects.create(payment_id="123", success=False)
        raise PaymentProcessingException("Not enough funds")
    else:
        PaymentRequest.objects.create(payment_id="123", success=True)


@pytest.mark.django_db
def test_models():
    assert PaymentRequest.objects.count() == 0


@pytest.mark.django_db
def test_successful_operation():
    with soft_atomic(safe_exceptions=(PaymentProcessingException,)):
        _process_payment(Decimal("15.00"))
    assert PaymentRequest.objects.filter(success=True).exists()


@pytest.mark.django_db
def test_failed_operation():
    with pytest.raises(PaymentProcessingException):
        with django.db.transaction.atomic():
            _process_payment(Decimal("150.00"))
    assert not PaymentRequest.objects.filter(success=False).exists()


@pytest.mark.django_db
def test_failed_operation_with_regular_atomic():
    with pytest.raises(PaymentProcessingException):
        with soft_atomic(safe_exceptions=(PaymentProcessingException,)):
            _process_payment(Decimal("150.00"))
    assert PaymentRequest.objects.exists()


@pytest.mark.django_db
def test_invalid_operation():
    with pytest.raises(ValueError):
        with soft_atomic(safe_exceptions=(PaymentProcessingException,)):
            _process_payment(Decimal("-5.00"))
    assert not PaymentRequest.objects.exists()


@pytest.mark.django_db
def test_constraints_break():
    with soft_atomic(safe_exceptions=(PaymentProcessingException,)):
        _process_payment(Decimal("15.00"))
    with pytest.raises(django.db.Error):
        with soft_atomic(safe_exceptions=(PaymentProcessingException,)):
            _process_payment(Decimal("15.00"))
    assert PaymentRequest.objects.count() == 1
