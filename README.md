# Excelegal Backend Repository

### _Steps to setup development server_

1. Create your virtual environment with python and install dependencies
```bash 
python -m venv .venv 
source ./.venv/bin/activate
pip install -r requirements.txt
```
2. Create a .env file with all the credentials and api secrets (take _.env.sample_ as sample) 
```bash
touch .env
```
3. Currently using default db provided by Django (_sqlite3_)
```bash
python manage.py migrate
```
4. ___Optional___: Create a superuser
```bash
python manage.py createsuperuser
```
5. Run server  
```bash
python manage.py runserver
```

###Swagger and Redoc api documentation at /swagger and /redoc
