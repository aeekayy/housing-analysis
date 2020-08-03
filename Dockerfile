FROM python:3.7-alpine
  
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev libffi-dev make
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

RUN apk --purge del .build-deps

EXPOSE 8080

ENTRYPOINT ["python3"]

CMD ["app.py"]
