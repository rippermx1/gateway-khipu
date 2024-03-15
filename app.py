from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi import Request
from models import PaymentRequest
from payment import KhipuPayment
from exceptions import PaymentException
from constants import FRONT_URL, FINISH_URL


khipu = KhipuPayment()
app = FastAPI()

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


@app.post("/create")
def create(request: PaymentRequest):
    url = f'{FRONT_URL}/payment/error'
    response = {'url': 'error'}
    try:
        print(request.model_dump())
        url = khipu.create(request.model_dump())
        print('url', url)
        if url:
            response = {'url': url}
        return response
    except PaymentException as e:
        print(e)
        return response


@app.get("/finish")
async def confirm(request: Request):
    id = request.query_params.get('id')
    status = request.query_params.get('status')
    try:
        trx = khipu.get(id)
        print('trx confirm', trx.status, trx.status_detail)
        khipu.update(id, {
            'status': trx.status,
            'status_detail': trx.status_detail
        })
        return RedirectResponse(f'{FRONT_URL}{FINISH_URL}?id={id}&status={status}',status_code=302)
    except PaymentException as e:
        print(e)
        return RedirectResponse(f'{FRONT_URL}{FINISH_URL}?id={id}&status={status}',status_code=302)


@app.get("/trx")
async def get_payment_db(request: Request):
    id = request.query_params.get('id')
    try:
        return khipu.getFromDB(id)
    except PaymentException as e:
        print(e)
        return {}


""" @app.post("/payment/trx")
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
        } """



# May be deprecated
""" @app.post("/payment/status")
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
            status_code=302) """

