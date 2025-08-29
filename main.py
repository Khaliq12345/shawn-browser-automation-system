import uvicorn


# Launch API
def main():
    # Start Fast API
    uvicorn.run(
        "src.api.app:app",
        host="localhost",
        port=8001,
        reload=False,
    )


if __name__ == "__main__":
    main()
    # celery -A src.utils.celery_app worker --loglevel=info
