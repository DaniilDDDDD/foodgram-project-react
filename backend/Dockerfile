FROM python:3.9.5

WORKDIR /code

COPY . /code

RUN pip install -r requirements.txt

RUN python manage.py collectstatic

RUN chmod +x run_server.sh

RUN ["sh", "run_server.sh"]

CMD gunicorn backend.wsgi:application --bind 0.0.0.0:8000