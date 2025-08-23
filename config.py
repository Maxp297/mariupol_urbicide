#!/usr/bin/env python3

import os
from pathlib import Path

PROJECT_ROOT = os.environ.get('PROJECT_ROOT', Path(__file__).resolve().parent)

db_config = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD', '')
}

if not db_config['host']:
    raise EnvironmentError("DB_HOST environment variable is not set")

if not db_config['database']:
    raise EnvironmentError("DB_NAME environment variable is not set")

if not db_config['user']:
    raise EnvironmentError("DB_USER environment variable is not set")
