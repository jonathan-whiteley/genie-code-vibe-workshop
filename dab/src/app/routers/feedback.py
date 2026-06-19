"""/api/feedback — themes, sentiment timeline, recent reviews."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from lib.config import get_settings
from lib.sql_utils import fetch_all

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


class ThemeRow(BaseModel):
    theme: str
    count_7d: int
    count_30d: int
    pct_negative_7d: float


class SentimentDay(BaseModel):
    date: str
    pos: int
    neu: int
    neg: int


class Review(BaseModel):
    feedback_id: str
    date: str
    store_id: str
    channel: str
    rating: int
    sentiment_label: str
    theme: str
    feedback_text: str
    needs_reply: bool
    ai_drafted_reply: str | None = None


@router.get("/themes", response_model=list[ThemeRow])
def themes() -> list[ThemeRow]:
    s = get_settings()
    cat, sch = s.catalog, s.schema_name
    rows = fetch_all(
        f"""
        WITH a AS (SELECT to_date(:anchor) AS d),
        recent AS (
          SELECT * FROM {cat}.{sch}.facts_customer_feedback, a
          WHERE date >= a.d - 30
        )
        SELECT theme,
               SUM(CASE WHEN date >= (SELECT d FROM a) - 7 THEN 1 ELSE 0 END) AS count_7d,
               COUNT(*) AS count_30d,
               ROUND(
                 SUM(CASE WHEN date >= (SELECT d FROM a) - 7 AND sentiment_label = 'neg' THEN 1 ELSE 0 END)
                 / NULLIF(SUM(CASE WHEN date >= (SELECT d FROM a) - 7 THEN 1 ELSE 0 END), 0) * 100,
                 1
               ) AS pct_negative_7d
        FROM recent
        GROUP BY theme
        ORDER BY count_30d DESC
        """,
        {"anchor": s.anchor_date},
    )
    return [ThemeRow(**r) for r in rows]


@router.get("/sentiment-timeline", response_model=list[SentimentDay])
def sentiment_timeline() -> list[SentimentDay]:
    s = get_settings()
    cat, sch = s.catalog, s.schema_name
    rows = fetch_all(
        f"""
        SELECT cast(date AS string) AS date,
               SUM(CASE WHEN sentiment_label = 'pos' THEN 1 ELSE 0 END) AS pos,
               SUM(CASE WHEN sentiment_label = 'neu' THEN 1 ELSE 0 END) AS neu,
               SUM(CASE WHEN sentiment_label = 'neg' THEN 1 ELSE 0 END) AS neg
        FROM {cat}.{sch}.facts_customer_feedback
        WHERE date >= date_sub(to_date(:anchor), 30)
        GROUP BY date
        ORDER BY date
        """,
        {"anchor": s.anchor_date},
    )
    return [
        SentimentDay(date=r["date"], pos=int(r["pos"] or 0), neu=int(r["neu"] or 0), neg=int(r["neg"] or 0))
        for r in rows
    ]


@router.get("/reviews", response_model=list[Review])
def reviews(limit: int = 5, needs_reply_only: bool = False) -> list[Review]:
    s = get_settings()
    cat, sch = s.catalog, s.schema_name
    where = "WHERE needs_reply = TRUE" if needs_reply_only else ""
    rows = fetch_all(
        f"""
        SELECT feedback_id, cast(date AS string) AS date, store_id, channel, rating,
               sentiment_label, theme, feedback_text, needs_reply, ai_drafted_reply
        FROM {cat}.{sch}.facts_customer_feedback
        {where}
        ORDER BY date DESC
        LIMIT {limit}
        """,
    )
    return [Review(**r) for r in rows]
