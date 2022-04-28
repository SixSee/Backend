from Excelegal import settings

bind = "0.0.0.0:8000"
wsgi_app = "Excelegal.wsgi:application"
reload = False
accesslog = '-'
workers = 3
graceful_timeout = 30
timeout = 30

if settings.DEBUG:
    reload = True
    timeout = 3600
    workers = 3
    threads = 1
