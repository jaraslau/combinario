#!/bin/sh

alembic upgrade head

python seed.py

uvicorn app:app --host 0.0.0.0 --port 8080 --loop uvloop --http httptools