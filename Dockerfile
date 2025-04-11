FROM python:3.12-slim-bullseye as builder

RUN apt-get update && apt-get install -y build-essential gcc curl
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y && apt-get install --reinstall libc6-dev -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN pip install --upgrade pip
COPY ./requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

FROM python:3.12.0-slim-bullseye

WORKDIR /src
RUN /usr/local/bin/python -m pip install --upgrade pip

COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY ./app /src/app

# Running the server through Uvicorn is better for handling the server
#   - Uvicorn is a web server / process manager used for running and managing daemon processes
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]