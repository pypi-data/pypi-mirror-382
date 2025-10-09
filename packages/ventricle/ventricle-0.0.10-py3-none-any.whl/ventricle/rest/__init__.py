from fastapi import FastAPI
from ._ping import ping_router


def create_rest_app(title:str="Ventricle",root_path: str = "") -> FastAPI:
    """
    Create and configure a FastAPI REST application.
    :param title: The title of the application.
    :param root_path: The root path of the application.
    :return: The configured FastAPI REST application.
    """
    app = FastAPI(title=title,root_path=root_path)

    app.include_router(ping_router)

    return app