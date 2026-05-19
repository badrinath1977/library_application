cd C:\Projects\Python-Library\MicroServices\AbsenceAPI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.sample .env
python run_server.py