from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi import Request
from models import PatientPaymentRequest, PaymentTrxId, BlockCreateRequest, BlockUpdateRequest, SpecialistAvailableHoursRequest
from payment import KhipuPayment
from exceptions import ConfirmationPaymentException, SpecialistException, SetDefaultScheduleDaysException, GetSpecialistScheduleException
from uuid import uuid4
from firebase import FirebaseAuth, FirebaseDatabase
from datetime import datetime
from logger import Logger
from constants import FRONT_URL, ERROR_URL, CONFIRM_URL


payment = KhipuPayment()
auth = FirebaseAuth()
db = FirebaseDatabase()
app = FastAPI()
logger = Logger()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/payment/create")
def create_payment(request: PatientPaymentRequest):
    patient = tuple()
    try:
        patient = db.get_patient_by_email(request.email)
        print("get patient", patient)

        if not patient:
            patient = db.create_patient(request)
            print('new patient', patient)

        payment_url = payment.create_payment({
            'subject': 'Terapia psicológica',
            'amount': 14990,
            'id': str(uuid4()),
            'body': 'Sesión de terapia psicológica online',
            'user_email': patient[1]['email'],
            'user_id': patient[0],
        })
        print('payment_url', payment_url)
        return {'payment_url': payment_url}
    except ConfirmationPaymentException as e:
        print(e)
        return RedirectResponse(
            f'{FRONT_URL}schedule-meet/payment/error',
            status_code=302)


@app.get("/payment/confirm")
async def confirm_payment(request: Request):
    trx_id = request.query_params.get('trx_id')
    user_id = request.query_params.get('user_id')
    try:
        trx = payment.get_payment(trx_id, user_id)
        print('trx confirm', trx.status, trx.status_detail)
        payment_updated = payment.update_payment(trx_id, {
            'user_id': user_id,
            'status': trx.status,
            'status_detail': trx.status_detail
        })
        print('payment_updated', payment_updated)
        return RedirectResponse(
            f'{FRONT_URL}{CONFIRM_URL}?trx_id={trx_id}&user_id={user_id}',
            status_code=302)
    except ConfirmationPaymentException as e:
        print(e)
        return RedirectResponse(
            f'{FRONT_URL}{ERROR_URL}?trx_id={trx_id}&user_id={user_id}',
            status_code=302)


@app.get("/payment/error")
async def error_payment(request: Request):
    trx_id = request.query_params.get('trx_id')
    user_id = request.query_params.get('user_id')
    trx = payment.get_payment(trx_id, user_id)
    payment_updated = payment.update_payment(trx_id, {
        'user_id': user_id,
        'status': trx.status,
        'status_detail': trx.status_detail
    })
    print('payment_updated', payment_updated)
    return RedirectResponse(
        f'{FRONT_URL}{ERROR_URL}?trx_id={trx_id}&user_id={user_id}',
        status_code=302)


@app.post("/payment/trx")
async def get_payment(request: PaymentTrxId):
    trx_id = request.trx_id
    user_id = request.user_id
    try:
        trx = payment.get_payment(trx_id, user_id)
        return {
            'status': trx.status,
            'status_detail': trx.status_detail
        }
    except ConfirmationPaymentException as e:
        print(e)
        return {
            'status': 'error',
            'status_detail': 'error'
        }


@app.post("/payment/trx/db")
async def get_payment_db(request: PaymentTrxId):
    trx_id = request.trx_id
    user_id = request.user_id
    try:
        trx = db.get_payment(trx_id, user_id)
        return trx
    except ConfirmationPaymentException as e:
        print(e)
        return {}


# May be deprecated
@app.post("/payment/status")
async def payment_status(request: PaymentTrxId):
    try:
        trx = payment.get_payment(request.trx_id)
        if trx.status == 'done':
            print(trx.payment_id, trx.status, trx.status_detail)
            payment.update_payment_status(payment)
            return {
                'status': payment.status,
                'status_detail': payment.status_detail
            }
        else:
            return {'status': 'pending', 'status_detail': 'pending'}
    except ConfirmationPaymentException as e:
        print(e)
        return RedirectResponse(
            f'{FRONT_URL}{ERROR_URL}?trx_id={trx_id}&user_id={user_id}',
            status_code=302)


# Specialist Endpoints
@app.post("/specialist/hours/available")
async def get_specialist_available_hours(
        request: SpecialistAvailableHoursRequest):
    try:
        hours = db.get_specialist_available_hours(
            request.user_id,
            request.date
        )
        return {
            'status': 'success',
            'hours': hours
        }
    except GetSpecialistScheduleException as e:
        logger.log(e)
        return {
            'status': 'error',
            'hours': []
        }


# Admin Settings Endpoints
@app.get("/schedule/days/default")
async def set_default_schedule_days():
    try:
        uuid = db.set_default_schedule_days()
        return {
            'status': 'success',
            'uuid': uuid
        }
    except SetDefaultScheduleDaysException as e:
        pass


# Patient Endpoints
@app.get("/patient")
async def get_patient(request: Request):
    user_id = request.query_params.get('user_id')
    return db.get_patient(user_id)
