#docker build . -t investing-dashboard:latest -f docker/Dockerfile && docker container prune -f && docker run -p 5006:5006 investing-dashboard:latest
FROM python:3.10.5-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY docker/requirements.txt .
RUN python -m pip install -r requirements.txt

COPY . /investing-dashboard
WORKDIR /

EXPOSE 5006:5006
ENTRYPOINT ["python3", "-m", "bokeh", "serve", "investing-dashboard/", "--allow-websocket-origin=*"]