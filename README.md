### Database setup
```bash
CREATE DATABASE jenova;
\c jenova
CREATE EXTENSION IF NOT EXISTS vector;
\dx;
CREATE USER jenova;
GRANT ALL PRIVILEGES ON DATABASE jenova TO jenova;
```
