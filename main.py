import uvicorn

def main():
    uvicorn.run(
        "src.api.app:app", 
        host="localhost",
        port=8001,
        reload=True,
    )

if __name__ == "__main__":
    main()

