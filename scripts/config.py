#!/usr/bin/env python3

import os

db_config = {
    'host': os.getenv('DB_HOST', 'forensic-db'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'mariupol_forensic'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD')
}