# AutoDeploy from Github Repository

An FastAPI application to automatically deploy Github Repositories on self-hosted server upon updates.

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

You can run the application in two ways:

1. Using Python directly:
```bash
python main.py
```

2. Using Uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```