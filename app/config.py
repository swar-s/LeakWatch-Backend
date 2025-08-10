import os


class Config:
    HIBP_API_KEY = os.getenv("HIBP_API_KEY")
    DEHASHED_API_KEY = os.getenv("DEHASHED_API_KEY")
    DEHASHED_EMAIL = os.getenv("DEHASHED_EMAIL")
    INTELX_API_KEY = os.getenv("INTELX_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MONGODB_URI = os.getenv("MONGODB_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
