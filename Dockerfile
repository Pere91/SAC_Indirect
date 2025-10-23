FROM python:3.12-alpine
WORKDIR /app
COPY player.py .
CMD [ "python", "-u", "player.py" ]