#web: gunicorn API.wsgi:application --log-file -
web: python manage.py collectstatic --noinput && gunicorn API.wsgi:application --log-file -