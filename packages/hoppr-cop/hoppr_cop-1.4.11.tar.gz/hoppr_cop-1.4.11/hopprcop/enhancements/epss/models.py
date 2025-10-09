"""EPSS API results model."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


class Datum(BaseModel):
    """Model to describe EPSS datum."""

    cve: str
    epss: str
    percentile: str
    date: str | None = None


class EPSSResult(BaseModel):
    """Model to describe an EPSS result."""

    status: str
    status_code: Annotated[int, Field(alias="status-code")]
    version: str
    access: str | None = None
    total: int | None = None
    offset: int | None = None
    limit: int | None = None
    data: list[Datum]
