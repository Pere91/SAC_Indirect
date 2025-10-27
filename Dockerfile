FROM python:3.12-alpine
WORKDIR /app
COPY board.py .
COPY player.py .
COPY exceptions.py .
COPY tictactoe.py .
