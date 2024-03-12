import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth
from uuid import uuid4
from datetime import datetime, date

app = firebase_admin.initialize_app(
    credentials.Certificate("./psicologaenlineasm-firebase.json"))


class FirebaseDatabase:
    def __init__(self):
        self.db = firestore.client(app)
        self.ref = None

    def get_specialist_available_hours(self, user_id: str, date: str):
        self.ref = self.db.collection(u'users').document(user_id)
        schedule = self.ref.collection(u'schedule').document(date).get()
        return list(schedule.to_dict()
                    .values()) if schedule.to_dict() else []

    def add_payment(self, payment):
        print('add_payment', payment)
        self.ref = self.db.collection(
            u'payments').document(payment['payment_id'])
        self.ref.set(payment)

    def get_payment(self, trx_id, user_id):
        print('get_payment', trx_id, user_id)
        self.ref = self.db.collection(u'patients').document(user_id)
        payment = self.ref.collection(u'payments').document(trx_id).get()
        print(payment.to_dict())
        return payment.to_dict() if payment else None

    def update_payment(self, id, data):
        self.ref = self.db.collection(u'patients').document(data['user_id'])
        self.ref.collection(u'payments').document(id).update(data)
        doc = self.ref.collection(u'payments').document(id).get()
        return doc.to_dict()

    def update_payment_status(self, payment_id, status, status_detail):
        print('update_payment_status', payment_id, status)
        self.ref = self.db.collection(u'payments').document(payment_id)
        return self.ref.update({
            'status': status,
            'status_detail': status_detail
        })

    def create_patient_payment(self, payment):
        self.ref = self.db.collection(u'patients').document(payment['user_id'])
        _, doc = self.ref.collection(u'payments').add(payment)
        print('create_patient_payment', doc.id)
        return doc.id

    def create_patient(self, patient):
        self.ref = self.db.collection(u'patients')
        _, doc = self.ref.add({
            "age": patient.age,
            "rut": patient.rut,
            "email": patient.email,
            "cellphone": patient.cellphone,
            "firstName": patient.firstName,
            "lastName": patient.lastName
        })
        print('firebase:create_patient', doc.id, doc.get().to_dict())
        return (doc.id, doc.get().to_dict()) if doc else None

    def add_user(self, user):
        print('add_user', user.uid)
        self.ref = self.db.collection(u'users').document(user.uid)
        self.ref.set({
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "phone_number": user.phone_number,
            "email_verified": user.email_verified,
            "disabled": user.disabled,
        })

    def get_patient(self, id):
        self.ref = self.db.collection(u'patients').document(id)
        return self.ref.get().to_dict()

    def get_patient_by_email(self, email):
        self.ref = self.db.collection(u'patients')
        query = self.ref.where("email", "==", email)
        for doc in query.stream():
            return (doc.id, doc.to_dict()) if query else None

    def get_user_by_email(self, email):
        print('get_user', email)
        self.ref = self.db.collection(u'users')
        query = self.ref.where("email", "==", email)
        return [doc.to_dict() for doc in query.stream()] if query else None

    ''' Use only for URGENCY.  Specialist can't be restored'''

    def delete_specialist(self, uuid: str):
        self.ref = self.db.collection(u'specialists').document(uuid)
        self.ref.delete()

    def set_default_schedule_days(self,):
        specialist_uuid = str(uuid4())
        self.ref_specialist = self.db.collection(
            u'specialists').document(specialist_uuid)
        self.ref_specialist.set({
            "first_name": "Admin",
            "last_name": "Admin",
            "email": "admin@admin.cl",
            "phone_number": "56912345678",
            "password": "admin",
            "is_admin": True,
            "is_specialist": True,
            "is_client": False,
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "is_online": False,
            "is_busy": False,
            "address": "Av. Siempre Viva 742",
            "city": "Santiago",
            "country": "Chile",
            "postal_code": "123456",
            "specialty": "Psicología",
            "sub_specialty": "Psicología Clínica",
            "bio": "",
            "photo_url": "",
            "price": 10000,
            "currency": "CLP",
            "uuid": specialist_uuid,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })

        schedule_uuid = str(uuid4())
        self.ref_schedule = self.db.collection(
            u'schedules').document(schedule_uuid)
        self.ref_schedule.set({
            "uuid": schedule_uuid,
            "specialist_uuid": specialist_uuid,
            "date": date.today().strftime("%Y-%m-%d"),
            "block_0": BLOCK_0,
            "block_1": BLOCK_1,
            "block_2": BLOCK_2,
            "block_3": BLOCK_3,
            "block_4": BLOCK_4,
            "block_5": BLOCK_5,
            "block_6": BLOCK_6,
            "block_7": BLOCK_7,
            "block_8": BLOCK_8,
            "block_9": BLOCK_9,
            "block_10": BLOCK_10,
            "block_11": BLOCK_11
        })

        return specialist_uuid


class FirebaseAuth:
    def create_user(self, email, password):
        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name='Patient',
                app=app
            )
            print('Successfully created new user:', user.uid)
            return user
        except Exception as error:
            print('Error creating new user:', error)
