
FROM python:3-alpine
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install pandas
COPY . .
EXPOSE 5001
CMD [ "flask", "run", "--host", "0.0.0.0", "--port", "5001" ]


