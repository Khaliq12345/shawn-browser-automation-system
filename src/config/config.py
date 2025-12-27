from dotenv import load_dotenv
import os

load_dotenv()

# Database
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
#Server config
SERVER_NAME =  os.getenv("SERVER_NAME", "server")
# AWS
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
# REDIS
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_URL = f"redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
# REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
# APP
ENV = os.getenv("ENV", "dev")
APP_PORT = os.getenv("APP_PORT", 8000)
HEADLESS = os.getenv("HEADLESS", "true")
# PROXY
PROXY_USERNAME = os.getenv("PROXY_USERNAME", "")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD", "")
RESIDENTIAL_PROXY_USERNAME = os.getenv("PROXY_RESIDENTIAL_USERNAME", "")
RESIDENTIAL_PROXY_PASSWORD = os.getenv("PROXY_RESIDENTIAL_PASSWORD", "")
# API KEY
API_KEY = os.getenv("API_KEY")
# PARSER
PARSER_URL = os.getenv("PARSER_URL")
PARSER_KEY = os.getenv("PARSER_KEY")
#SLACK
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
#SCHEDULE HOURS
MINUTES = int(os.getenv("MINUTES", 60))
#DEAL_WITH_NULL_ONLY
ONLY_NULL = os.getenv("ONLY_NULL", "yes")
#PARSE OUTPUT
PARSE_OUTPUT = os.getenv("PARSE_OUTPUT", "no")
