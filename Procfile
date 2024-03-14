release: python src/manage.py migrate --run-syncdb
release: python src/manage.py collectstatic --noinput
web: cd src && gunicorn djangoProject.wsgi