from ninja import Router

router = Router()

from . import POST  # noqa: E402, F401

__all__ = ['router']
