import uvicorn

if __name__ == "__main__":
    uvicorn.run("web:server", host="127.0.0.1", port=8000, factory=True, reload=True)



