from datetime import datetime
import uvicorn


# Launch API
def main():
    uvicorn.run(
        "src.api.app:app",
        host="localhost",
        port=8002,
        reload=True,
    )


if __name__ == "__main__":
    main()
