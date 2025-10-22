from google import genai
import sys, os

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.config import AppConfig

config = AppConfig()
client = genai.Client(api_key=config.gemini.api_key, http_options={"api_version": "v1"})

print("Listing models (v1):")
models = client.models.list()
for m in models:
    try:
        to_dict = getattr(m, 'to_dict', None)
        if callable(to_dict):
            md = to_dict()
            print(md.get('name'), '| methods:', md.get('supported_generation_methods'))
        else:
            print(getattr(m, 'name', m))
    except Exception as e:
        print('ERR model:', e)