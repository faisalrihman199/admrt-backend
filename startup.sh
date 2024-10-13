 #!/bin/bash
# python manage.py migrate && python manage.py collectstatic && gunicorn --workers 2 admrt.wsgi



python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8080 && python3 manage.py runserver 0.0.0.0:8080 collectstatic --noinput && waitress-serve --listen=0.0.0.0:8080 admrt.wsgi:application
