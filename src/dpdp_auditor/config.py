import os
from dotenv import load_dotenv
load_dotenv()
def get_api_key() -> str:
    key=os.getenv("DEEPSEEK_API_KEY")  #I put secret key as sk-123456
    # print(f"MY secret is: {key}") 
    if key is None or key=='':
        raise ValueError("DEEPSEEK_API_KEY is missing from .env")
    return key