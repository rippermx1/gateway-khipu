import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid
import os
import json

path = "./default.json"
firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')
print(firebase_credentials)

if firebase_credentials:
    with open("default.json", "w") as write_file:
            json.dump(firebase_credentials, write_file)
app = firebase_admin.initialize_app(credentials.Certificate(path))


class FirebaseDatabase:
    PAYMENTS = 'payments'
    
    def __init__(self):
        self.db = firestore.client(app)
        self.ref = None


    def create(self, payment):
        doc = None
        index = 1
        try:
            payment['uuid'] = uuid.uuid4().hex
            doc = self.db.collection(f'{self.PAYMENTS}').add(payment)
            return doc[index]
        except Exception as e:
            print(e)
            return doc[index]

    def get(self, id):
        payment = self.db.collection(f'{self.PAYMENTS}').document(id).get()
        print(payment.to_dict())
        return payment.to_dict() if payment else None

    def update(self, id, payment):
        self.db.collection(f'{self.PAYMENTS}').document(id).update(payment)

    def update_payment_status(self, payment_id, status, status_detail):
        print('update_payment_status', payment_id, status)
        self.ref = self.db.collection(u'payments').document(payment_id)
        return self.ref.update({
            'status': status,
            'status_detail': status_detail
        })