import uvicorn



def run_server():
    uvicorn.run(
        "server.service:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
)

if __name__ == "__main__":

    run_server()
