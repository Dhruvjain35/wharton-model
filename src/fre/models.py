"""Core records. Every number the engine shows is one of these, never a bare float."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class FactStatus(str, Enum):
    REPORTED = "reported"
    DERIVED = "derived"
    ANALYST_ADJUSTED = "analyst-adjusted"
    MISSING = "missing"
    CONFLICTING = "conflicting"


class Company(BaseModel):
    model_config = ConfigDict(frozen=True)

    cik: str
    legal_name: str
    tickers: list[str]
    fiscal_year_end: str  # MMDD as reported in SEC submissions, e.g. "1231"
    currency: str = "USD"


class Source(BaseModel):
    """Where a reported value came from, precise enough for a teammate to open it."""

    model_config = ConfigDict(frozen=True)

    accession: str
    form: str
    filed: date
    url: str
    locator: str  # XBRL tag ("us-gaap:Revenues") or filing table/page reference
    snapshot_id: str  # sha256 prefix of the immutable raw snapshot the value was read from
    retrieved_at: str
    accepted: str | None = None  # EDGAR acceptance timestamp from the filing index


class Restatement(BaseModel):
    """An older filing reported a different value for the same period."""

    model_config = ConfigDict(frozen=True)

    accession: str
    filed: date
    value: float
    reason: str  # e.g. "20-for-1 stock split effective 2022-07-15" or "unexplained"


class Fact(BaseModel):
    model_config = ConfigDict(frozen=True)

    company: str  # CIK
    metric: str
    value: float | None
    unit: str  # "USD", "USD/shares", "shares", "pure"
    scale: int = 1  # presentation scale in the filing (1e6 for "$ in Millions"); values are stored unscaled
    currency: str | None = "USD"  # None for share counts
    period_start: date | None  # None for balance-sheet (instant) facts
    period_end: date
    fiscal_label: str  # "FY2025"
    status: FactStatus
    sources: list[Source] = Field(default_factory=list)
    formula: str | None = None  # for derived facts
    inputs: list[str] = Field(default_factory=list)  # fact keys a derived value depends on
    restated_from: list[Restatement] = Field(default_factory=list)
    candidates: list[float] = Field(default_factory=list)  # visible when CONFLICTING
    notes: list[str] = Field(default_factory=list)

    @property
    def key(self) -> str:
        return f"{self.metric}@{self.fiscal_label}"


class ReviewItem(BaseModel):
    """Something a human must look at before the number is trusted."""

    model_config = ConfigDict(frozen=True)

    severity: Literal["block", "warn", "info"]
    metric: str
    fiscal_label: str | None
    kind: str  # missing | conflicting | restated | tag-switch | split-adjusted | scope-change | ...
    message: str


class Adjustment(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    metric: str
    fiscal_label: str
    original: float
    delta: float
    category: str
    rationale: str
    evidence: str
    author: str
    status: Literal["proposed", "approved", "rejected"]
    reviewer: str | None = None

    @property
    def resulting(self) -> float:
        return self.original + self.delta


class Assumption(BaseModel):
    model_config = ConfigDict(frozen=True)

    driver: str
    value: float
    low: float
    high: float
    units: str
    rationale: str
    source: str | None = None
    owner: str
    as_of: date
    status: Literal["proposed", "approved"] = "proposed"
