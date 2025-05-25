import uvicorn

from src.config.settings import Settings
from src.logger import make_logger
from src.web_app.main import WebApplication

logger = make_logger(__name__)

settings = Settings()


def create_app():
    """ファクトリー関数"""
    web_app = WebApplication()
    return web_app.app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
