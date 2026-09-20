from openai import OpenAI

from audio_api.environment import OPEN_API_KEY_ENV

OPENAI_CLIENT = OpenAI(api_key=OPEN_API_KEY_ENV)
