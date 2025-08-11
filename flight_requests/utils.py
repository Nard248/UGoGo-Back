import random
import string


def generate_verification_code(code_type='pickup'):
    """Generate unique 4-digit codes for pickup or delivery"""
    code = ''.join(random.choices(string.digits, k=4))

    from flight_requests.models.request import Request

    if code_type == 'pickup':
        while Request.objects.filter(
            pickup_verification_code=code,
            status__in=['in_process', 'in_transit']
        ).exists():
            code = ''.join(random.choices(string.digits, k=4))
    elif code_type == 'delivery':
        while Request.objects.filter(
            delivery_verification_code=code,
            status='in_transit'
        ).exists():
            code = ''.join(random.choices(string.digits, k=4))

    return code
