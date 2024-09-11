FROM python:3.12-alpine
ENV APP_HOME=/app
WORKDIR $APP_HOME

COPY . .

RUN pip install -r requirements.txt
RUN rm -rf /root/.cache

EXPOSE 5000
EXPOSE 3000

ENTRYPOINT [ "python", "main.py" ]
