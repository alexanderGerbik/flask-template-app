FROM python:3.7-slim

RUN pip install --no-cache-dir --disable-pip-version-check poetry

RUN groupadd -g 1000 appgroup
RUN useradd -g appgroup -u 1000 --create-home appuser
USER appuser:appgroup

ENV VIRTUAL_ENV=/home/appuser/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY --chown=appuser:appgroup pyproject.toml poetry.lock /home/appuser/
RUN poetry install --no-dev

COPY --chown=appuser:appgroup migrations alembic.ini /home/appuser/
COPY --chown=appuser:appgroup src /home/appuser/app

ENV PYTHONPATH=/home/appuser/app FLASK_APP=service FLASK_ENV=production
ENV DATABASE_URL=postgresql://user:password@host:port/database-name

WORKDIR /home/appuser
CMD ["gunicorn", "-c", "python:gunicorn_conf", "service.wsgi:app"]
