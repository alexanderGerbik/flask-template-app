# Flask template app

Just a suite of approaches which I find useful.

## Commands

Run database schema migrations:
```bash
alembic upgrade head
```

Generate secret key:
```bash
tr -dc 'a-z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c50
```

Generate RSA private/public key pair:
```bash
openssl genrsa -out private_key_file.pem 4096
openssl rsa -in private_key_file.pem -outform PEM -pubout -out public_key_file.pem
```

## Run unit tests
1. Install [poetry](https://python-poetry.org/docs/)
1. Install project dependencies (run in the root directory):
    ```bash
    poetry install
    ```
1. Set following environment variables (use `.env` file):
    ```bash
    export PYTHONPATH=src
    # optional: export TEST_DATABASE_URL=postgresql://postgres:password@localhost:port/test_db_name
    ```
1. Run tests:
    ```bash
    poetry run pytest
    ```
    or
    ```bash
    poetry shell
    pytest
    ```
