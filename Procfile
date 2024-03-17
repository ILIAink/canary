release: python src/manage.py migrate && python src/manage.py collectstatic --noinput
web: cd src && gunicorn djangoProject.wsgi