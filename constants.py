import os
heroku_app_name = os.getenv('HEROKU_APP_NAME')


CURRENCY_CLP = 'CLP'
FRONT_URL = 'http://localhost:5173'
FINISH_URL = '/checkout/finish'
API_URL = f'https://{heroku_app_name}.herokuapp.com' if heroku_app_name else 'http://127.0.0.1:8000'
