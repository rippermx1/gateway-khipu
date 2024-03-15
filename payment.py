from pykhipu.client import Client
from exceptions import KhipuGetBanksException
from constants import CURRENCY_CLP, API_URL
from firebase import FirebaseDatabase


class KhipuPayment():
    def __init__(self):
        self.client = Client(
            receiver_id='433491',
            secret='86db469310a35b26a914514917915cf5db7fbd3c'
        )
        self.db = FirebaseDatabase()

    def get_banks(self):
        try:
            banks_list = []
            # BankItem = bank_id | name | message | min_amount | bank_type | parent
            banks = self.client.banks.get().banks
            return [banks_list.append({'id': b.bank_id, 'name': b.name}) for b in banks]
        except KhipuGetBanksException as e:
            print(e)
            return None

    def get_status(self, trx_id):
        return self.client.payments.get_id(trx_id)

    # Done
    def create(self, payment: dict) -> str:
        try:
            aux = self.db.create(payment)
            trx = self.client.payments.post(
                subject=payment.get('type'),
                currency=CURRENCY_CLP,
                amount=payment.get('amount'),
                transaction_id=aux.id,
                return_url=f'{API_URL}/finish?id={aux.id}&status=done',
                cancel_url=f'{API_URL}/finish?id={aux.id}&status=cancel',
                picture_url='https://images.deepai.org/machine-learning-models/0c7ba850aa2443d7b40f9a45d9c86d3f/text2imgthumb.jpeg',
                body=payment.get('description'),
            )
            print('trx', trx)
            payment['trx_id'] = trx.payment_id
            payment['url'] = trx.payment_url
            payment['status'] = None
            payment['status_detail'] = None
            self.db.update(aux.id, payment)
            
            return trx.payment_url
        except Exception as e:
            print(e)
            return None

    # Done
    def update(self, id, payment):
        try:
            self.db.update(id, payment)
        except Exception as e:
            print(e)
            return None

    # Done
    def get(self, id):
        try:
            payment = self.db.get(id)
            print('get_payment_from_db', payment)
            return self.client.payments.get_id(payment['trx_id'])
        except Exception as e:
            print(e)
            return None
        
    
    def getFromDB(self, id):
        try:
            return self.db.get(id)
        except Exception as e:
            print(e)
            return None

    def update_payment_status(self, payment):
        try:
            self.db.update_payment_status(
                payment.payment_id, payment.status, payment.status_detail)
        except Exception as e:
            pass
