# FROM python:3.7-alpine3.8
FROM python:3.8.3-alpine3.11
RUN apk --no-cache add build-base
RUN apk --no-cache add postgresql-dev
RUN mkdir /app
ARG project_dir=/app
ADD api05.py $project_dir
WORKDIR $project_dir
RUN pip install flask
RUN python3 -m pip install psycopg2
ENV FLASK_APP=api05.py
ENTRYPOINT ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
