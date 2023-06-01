FROM python

WORKDIR /app

COPY trial.py .

RUN pip install yfinance pandas requests

CMD [ "python", "./trial.py" ]