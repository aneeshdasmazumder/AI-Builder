import os
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import requests

url = 'https://api.openwebninja.com/job-salary-data/job-salary'
params = {
    'job_title': 'nodejs developer',
    'location': 'New York'
}

env_path = Path.cwd().parent / '.env'
if not env_path.exists():
    env_path = Path(find_dotenv())

load_dotenv(env_path, override=True)
api_key = os.getenv('OPENWEBNINJA_API_KEY', '').strip()
if not api_key:
    raise RuntimeError('OPENWEBNINJA_API_KEY was not found in .env')
if api_key.startswith('••'):
    raise RuntimeError('The API key is still masked. Paste the real key into .env, not the bullets from Postman.')

headers = {
    'x-api-key': api_key,
    'Accept': 'application/json'
}

def _getMarketSalaryData():
    respone = requests.get(url, headers=headers, params=params, timeout=20)
    respone.raise_for_status()
    data = respone.json()
    return data

if __name__ == "__main__":
    print(_getMarketSalaryData())
