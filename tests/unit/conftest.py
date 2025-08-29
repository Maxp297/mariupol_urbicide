import os

# Dummy values for env vars
def pytest_configure():
    os.environ.setdefault("DB_HOST", "localhost")
    os.environ.setdefault("DB_NAME", "testdb")
    os.environ.setdefault("DB_USER", "testuser")
    os.environ.setdefault("DB_PASSWORD", "secret")
