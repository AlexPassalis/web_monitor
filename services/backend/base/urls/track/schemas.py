from ninja import Schema
from pydantic import HttpUrl


class TrackRequest(Schema):
    url: HttpUrl


class TrackResponse(Schema):
    message: str
    url: str


class ValidationErrorResponse(Schema):
    detail: list[dict]
