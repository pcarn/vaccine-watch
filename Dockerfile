from python:3.9
WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONUNBUFFERED 1
ENTRYPOINT [ "python", "clock.py" ]
