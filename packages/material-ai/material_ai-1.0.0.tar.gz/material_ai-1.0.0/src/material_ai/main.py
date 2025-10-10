import uvicorn
from .app import get_app

if __name__ == "__main__":
    uvicorn.run(
        get_app(),
        host="0.0.0.0",
        port=8080,
        lifespan="auto",
        log_level="info",
        reload=True,
    )
