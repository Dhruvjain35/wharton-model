"""Accounting review ledger (PRD A4).

Adjustments live in reviews/<TICKER>/adjustments.yaml. Each one states its delta as
arithmetic over verified facts from the same fiscal year, so no adjusted number is
ever typed by hand. The AI may propose; only a named human reviewer who is not the
author may approve. Only approved adjustments apply, and all of them can be
switched off at once. The reported dataset is never modified.
"""

from __future__ import annotations

import ast
import copy
import operator
import re
from pathlib import Path

import yaml

from .models import Adjustment, FactStatus
from .normalize import Dataset

ROOT = Path(__file__).resolve().parents[2]
AI_NAMES = ("claude", "ai", "gpt", "llm", "model")


class LedgerError(ValueError):
    pass


# PRD A4 review categories (plus two observation-only ones)
CATEGORIES = {"recurring-called-one-time", "restructuring", "legal", "investment-gains", "unusual-tax",
              "depreciation-assumptions", "working-capital-and-tax-timing", "scope-change", "stock-compensation"}


_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.USub: operator.neg, ast.UAdd: operator.pos}


def evaluate(expr: str, names: dict[str, float]) -> float:
    """+ - * / and parentheses over numbers and fact names. Nothing else parses."""

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return float(node.value)
        if isinstance(node, ast.Name):
            if node.id not in names:
                raise LedgerError(f"formula references missing or unresolved fact '{node.id}'")
            return names[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.operand))
        raise LedgerError(f"not allowed in an adjustment formula: {ast.dump(node)[:60]}")

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise LedgerError(f"cannot parse formula {expr!r}") from e
    return ev(tree)


def _evidence_text(ev) -> str:
    if isinstance(ev, dict):
        return f"{ev.get('source', '')} [{ev.get('snapshot_id', '')}]: \"{ev.get('quote', '')}\"".strip()
    return str(ev)


def _is_ai(name: str | None) -> bool:
    return bool(name) and any(tok in AI_NAMES for tok in re.findall(r"[a-z]+", name.lower()))


def build(ds: Dataset, entries: list[dict]) -> list[Adjustment]:
    out = []
    for e in entries:
        label = e["fiscal_label"]
        if label not in ds.labels:  # outside this run's window (e.g. an as-of run): not applicable
            continue
        names = {k.split("@")[0]: f.value for k, f in ds.facts.items()
                 if k.endswith(f"@{label}") and f.value is not None}
        if e["category"] not in CATEGORIES:
            raise LedgerError(f"{e['id']}: category '{e['category']}' is not one of {sorted(CATEGORIES)}")
        if e["metric"] not in names:
            raise LedgerError(f"{e['id']}: target {e['metric']}@{label} is missing")
        if e["status"] == "approved":
            r = e.get("reviewer")
            if not r or r == e["author"] or _is_ai(r):
                raise LedgerError(f"{e['id']}: approval needs a human reviewer other than the author")
        scope = dict(names)
        for cname, c in (e.get("constants") or {}).items():
            if not c.get("quote"):
                raise LedgerError(f"{e['id']}: constant '{cname}' needs a verbatim filing quote")
            scope[cname] = float(c["value"])
        for aname, a in (e.get("assumptions") or {}).items():
            if not a.get("rationale"):
                raise LedgerError(f"{e['id']}: assumption '{aname}' needs a rationale")
            scope[aname] = float(a["value"])
        out.append(Adjustment(id=e["id"], metric=e["metric"], fiscal_label=label, original=names[e["metric"]],
                              delta=evaluate(e["delta_formula"], scope), category=e["category"],
                              rationale=e["rationale"], evidence=_evidence_text(e["evidence"]), author=e["author"],
                              status=e["status"], reviewer=e.get("reviewer")))
    return out


def _money_phrases(value: float) -> list[str]:
    """How a filing would write this amount: $2.1 billion, $796 million, $1,396 million."""
    out = []
    if abs(value) >= 1e9:
        b = abs(value) / 1e9
        out += [f"${b:.1f} billion", f"${b:g} billion", f"$ {b:.1f} billion", f"$ {b:g} billion"]
    m = abs(value) / 1e6
    out += [f"${m:,.0f} million", f"${m:.0f} million", f"$ {m:,.0f} million", f"{m:,.0f}"]
    return out


def _figure_in(quote: str, v: float) -> bool:
    """The value appears as a whole number in millions, or as the same value rounded to $x.x billion."""
    millions = re.escape(f"{abs(v) / 1e6:,.0f}")
    if re.search(rf"(?<![\d,.]){millions}(?![\d,]|\.\d)", quote):
        return True
    b = f"{abs(v) / 1e9:.1f}"
    return abs(v) >= 1e9 and re.search(rf"\$ ?{re.escape(b)} billion", quote) is not None


def verify_quotes(entries: list[dict], text_for, ds: Dataset | None = None) -> list[str]:
    """Every quote must appear verbatim in its snapshot and contain the number it supports."""
    problems = []
    for e in entries:
        ev = e.get("evidence")
        if isinstance(ev, dict) and ev.get("quote"):
            quote = " ".join(ev["quote"].split())
            if quote not in text_for(ev["snapshot_id"]):
                problems.append(f"{e['id']}.evidence: quote not found verbatim in snapshot {ev['snapshot_id']}")
            elif ev.get("fact") and ds is not None:
                v = ds.value(ev["fact"], e["fiscal_label"])
                if v is None or not _figure_in(quote, v):
                    problems.append(f"{e['id']}.evidence: {ev['fact']}@{e['fiscal_label']} value not in its quote")
        for cname, c in (e.get("constants") or {}).items():
            quote = " ".join(c["quote"].split())
            if quote not in text_for(c["snapshot_id"]):
                problems.append(f"{e['id']}.{cname}: quote not found verbatim in snapshot {c['snapshot_id']}")
            elif not any(re.search(rf"(?<![\d,.]){re.escape(p)}(?![\d]|\.\d)", quote) for p in _money_phrases(float(c["value"]))):
                problems.append(f"{e['id']}.{cname}: value {float(c['value']) / 1e9:g}bn does not appear in its quote")
    return problems


def load(ds: Dataset, ticker: str) -> tuple[list[Adjustment], list[dict]]:
    path = ROOT / "reviews" / ticker / "adjustments.yaml"
    if not path.exists():
        return [], []
    doc = yaml.safe_load(path.read_text()) or {}
    return build(ds, doc.get("adjustments") or []), doc.get("observations") or []


def apply(ds: Dataset, adjustments: list[Adjustment], *, enabled: bool = True,
          statuses: tuple[str, ...] = ("approved",)) -> Dataset:
    out = copy.deepcopy(ds)
    if not enabled:
        return out
    for a in adjustments:
        if a.status not in statuses:
            continue
        _shift(out, a.metric, a.fiscal_label, a.delta, a)
        if a.metric == "net_income":
            _shift(out, "net_income_to_common", a.fiscal_label, a.delta, a)
            for eps, shares in (("eps_diluted", "shares_diluted"), ("eps_basic", "shares_basic")):
                sh = out.value(shares, a.fiscal_label)
                key = f"{eps}@{a.fiscal_label}"
                if sh:
                    _shift(out, eps, a.fiscal_label, a.delta / sh, a, note=f"delta / {shares}")
                elif key in out.facts:
                    # never leave the reported EPS standing next to an adjusted net income
                    f = out.facts[key]
                    out.facts[key] = f.model_copy(update={"value": None, "status": FactStatus.MISSING, "notes": f.notes + [
                        f"{a.id}: adjusted EPS unavailable because {shares}@{a.fiscal_label} is missing"]})
    return out


def _shift(ds: Dataset, metric: str, label: str, delta: float, a: Adjustment, note: str = "") -> None:
    key = f"{metric}@{label}"
    f = ds.facts.get(key)
    if f is None or f.value is None:
        return
    ds.facts[key] = f.model_copy(update={
        "value": f.value + delta,
        "status": FactStatus.ANALYST_ADJUSTED,
        "notes": f.notes + [f"{a.id} ({a.category}, {a.status}): {delta:+,.4g} {note}".rstrip()],
    })
