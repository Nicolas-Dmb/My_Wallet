release: "python API/manage.py collectstatic --noinput"
web: gunicorn API.API.wsgi:application --log-file -