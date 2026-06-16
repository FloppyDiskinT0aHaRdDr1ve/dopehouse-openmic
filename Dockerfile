FROM python:3.12-slim

LABEL maintainer="Jacob Daniel Powell"
LABEL description="DOPEHOUSE OPENMIC - AI Music Creation Platform"

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir .

CMD ["dopehouse-openmic", "--transport", "http", "--port", "8000"]
