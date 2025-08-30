import uvicorn
from src.config.config import ENV, APP_PORT


# Launch API
def main():
    # Start Fast API
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=int(APP_PORT),
        reload=ENV == "dev",
    )


if __name__ == "__main__":
    main()
    # celery -A src.utils.celery_app worker --loglevel=info
