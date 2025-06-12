FROM python:3.11.8-slim-bookworm
COPY requirements.txt /app/requirements.txt
RUN pip install --require-hashes -r /app/requirements.txt --no-deps
ENV GOOGLE_APPLICATION_CREDENTIALS app/service_account.json
ENTRYPOINT ["text-categorizer"]
