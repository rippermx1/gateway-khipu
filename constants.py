import os
heroku_app_name = os.getenv('HEROKU_APP_NAME')
front_url = os.getenv('FRONT_URL')


CURRENCY_CLP = 'CLP'
FRONT_URL = front_url if front_url else 'http://localhost:5173'
FINISH_URL = '/checkout/finish'
API_URL = f'https://{heroku_app_name}.herokuapp.com' if heroku_app_name else 'http://127.0.0.1:8000'
