set -e

python manage.py migrate --noinput
#python manage.py setup_oauth

if [ "$DEBUG" == "1" ]; then
  python manage.py runserver 0.0.0.0:8000
else
  gunicorn --bind=0.0.0.0:8000 --workers=3 --max-requests=1000 --log-level=error config.wsgi:application
fi
