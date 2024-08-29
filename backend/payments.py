import uuid
from config import WEBAPP_URL
from yookassa import Configuration, Payment

Configuration.account_id = '986380'
Configuration.secret_key = 'test_-w98haY35KjI84lesPQXdgNsi9JigfJWkiQPo_UfDr8'

def create_payment(plan, user_id):
    payment = Payment.create({
        "amount": {
            "value": str(plan.price)+'.00',
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": WEBAPP_URL + '/succeeded'
        },
        "capture": True,
        "description": "Оплата",
        'metadata': {
            'plan': plan.id,
            'user_id': user_id
        }
    }, uuid.uuid4())
    
    return payment.confirmation.confirmation_url
