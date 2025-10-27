from ninja import Router

track_router = Router()

from . import POST  # noqa: E402, F401

__all__ = ['track_router']
