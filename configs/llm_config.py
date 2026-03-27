import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# LiteLLM Proxy 설정
LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:4000")
MODEL_NAME = "gpt-4o-mini"
SEED = 42
TEMPERATURE = 0.0  # 재현성 완벽 보장