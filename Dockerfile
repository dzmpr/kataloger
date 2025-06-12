FROM python:3.13-alpine

RUN python -m venv /venv
RUN /venv/bin/pip install --upgrade pip
RUN /venv/bin/pip install --no-cache-dir kataloger
ENV PATH="/venv/bin:$PATH"

WORKDIR /project

ENTRYPOINT ["kataloger"]
