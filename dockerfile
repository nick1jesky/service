FROM python:3.14.0

WORKDIR /service

COPY ./order_item_control/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./order_item_control/ .

CMD ["python", "main.py"]