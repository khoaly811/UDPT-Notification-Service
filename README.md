# UDPT-Hospital-Management-System-Notification-Service

Setup

Requirement: Python version <3.12 and >=3.11.0

Install poetry
```bash
python -m pip install poetry==2.1.3
```

Install dependencies:
```bash 
poetry install
```

Initialize databases:
```bash
poetry run task up
```

Start sever:
```bash
poetry run task start
```

Clean up databases:
```bash
poetry run task down
```