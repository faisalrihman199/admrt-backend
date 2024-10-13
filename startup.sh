 #!/bin/bash
# python manage.py migrate && python manage.py collectstatic && gunicorn --workers 2 admrt.wsgi

source venv/bin/activate

python manage.py migrate && python manage.py runserver 0.0.0.0:8080 && python manage.py runserver 0.0.0.0:8080 collectstatic --noinput && waitress-serve --listen=0.0.0.0:8080 admrt.wsgi:application
