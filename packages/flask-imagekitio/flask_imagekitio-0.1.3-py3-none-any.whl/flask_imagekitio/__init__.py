from contextlib import contextmanager
from typing import Generator, Optional

from flask import Flask
from imagekitio import ImageKit  # type: ignore


class ImagekitIO:
    public_key: Optional[str]
    url_endpoint: Optional[str]
    __private_key: Optional[str]

    def __init__(self, app: Optional[Flask] = None) -> None:
        self.public_key = None
        self.url_endpoint = None
        self.__private_key = None
        if app:
            self.init_app(app)

    @contextmanager
    def interface(self) -> Generator[ImageKit, None, None]:
        imagekit = None
        try:
            imagekit = self.__ik()
            yield imagekit
        except AttributeError as e:
            raise AttributeError(f"In order to use the interface you must correctly configure this extension. {e}")
        finally:
            del imagekit

    def __ik(self) -> ImageKit:
        if not self.public_key or not self.__private_key or not self.url_endpoint:
            raise AttributeError(
                "You must set config variables `IMAGEKITIO_URL_ENDPOINT`, `IMAGEKITIO_PRIVATE_KEY` and `IMAGEKITIO_PUBLIC_KEY` in order to initialize this extension"
            )
        return ImageKit(self.public_key, self.__private_key, self.url_endpoint)

    def init_app(self, app: Flask) -> None:
        if not app.config.get("IMAGEKITIO_URL_ENDPOINT", None) or not app.config.get("IMAGEKITIO_PRIVATE_KEY", None) or not app.config.get("IMAGEKITIO_PUBLIC_KEY", None):
            raise AttributeError("You must set config variables `IMAGEKITIO_URL_ENDPOINT`, `IMAGEKITIO_PRIVATE_KEY` and `IMAGEKITIO_PUBLIC_KEY`")

        if "imagekitio" in app.extensions:
            raise RuntimeError("ImageKitIO extension is already registered on this Flask app.")

        app.extensions["imagekitio"] = self

        self.url_endpoint = app.config.get("IMAGEKITIO_URL_ENDPOINT")
        self.public_key = app.config.get("IMAGEKITIO_PUBLIC_KEY")
        self.__private_key = app.config.get("IMAGEKITIO_PRIVATE_KEY")

        return None
