release: python manage.py migrate --run-syncdb
release: python manage.py collectstatic --noinput
web: gunicorn djangoProject.wsgi