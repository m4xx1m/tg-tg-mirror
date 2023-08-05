FROM python:3.11.4-alpine3.18 as builder

WORKDIR /builder

RUN pip install --no-cache-dir --upgrade pip wheel

COPY requirements.txt .
RUN python -m pip wheel --no-cache-dir --wheel-dir=./wheels -r requirements.txt


FROM python:3.11.4-alpine3.18

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY --from=builder /builder/wheels wheels
RUN python -m pip install --no-cache wheels/* && rm -rf wheels

COPY main.py /app/

CMD ["python", "main.py"]
