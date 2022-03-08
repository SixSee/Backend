# Excelegal Backend Repository
### Swagger and Redoc api documentation at /swagger and /redoc

### _Steps to setup development server_

1. Create your virtual environment with python and install dependencies
```bash 
python -m venv .venv 
source ./.venv/bin/activate
pip install -r requirements.txt
```
2. Create a env.py file with all the credentials and api secrets (take _.env.sample_ as sample) 
```bash
touch env.py
```
3. Fill env variables
 ```python
DEBUG = True/False
NADMIN_USERS = 3
SECRET = "secret"
GOOGLE_CLIENT_ID = "client_id"
GOOGLE_CLIENT_SECRET = "client_secret"
```

5. Currently using default db provided by Django (_sqlite3_)
```bash
python manage.py migrate
```
5. ___Optional___: Create a superuser
```bash
python manage.py createsuperuser
```
6. Run server  
```bash
python manage.py runserver
```