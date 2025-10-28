from ninja import Router

router_track = Router()

from . import POST  # noqa: E402, F401

__all__ = ['router_track']
