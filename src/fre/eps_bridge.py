"""Where EPS growth came from (PRD A3).

    EPS factor  ~=  net-income factor / diluted-share factor

In logs the identity is additive, so each year's EPS growth splits exactly into
an earnings part, a share-count part, and a residual (rounding, allocation among
share classes, numerator differences). The residual is reported, never hidden.

Buybacks are shown next to their cash cost and next to SBC. A shrinking share
count is not free growth: the cash spent on it is cash not reinvested or held.
"""

from __future__ import annotations

import math

from .normalize import Dataset

RECOMPUTE_TOLERANCE = 0.02  # dollars per share; EPS is reported to the cent


def _numerator(ds: Dataset, label: str, other: str) -> tuple[str, float | None]:
    """Net income to common when BOTH years report it; otherwise net income in both years."""
    if ds.value("net_income_to_common", label) is not None and ds.value("net_income_to_common", other) is not None:
        return "net_income_to_common", ds.value("net_income_to_common", label)
    return "net_income", ds.value("net_income", label)


def bridge(ds: Dataset) -> list[dict]:
    rows = []
    for prev, cur in zip(ds.labels, ds.labels[1:]):
        num_name_c, ni_c = _numerator(ds, cur, prev)
        num_name_p, ni_p = _numerator(ds, prev, cur)
        need = {f"{num_name_c}@{cur}": ni_c, f"{num_name_p}@{prev}": ni_p,
                f"shares_diluted@{cur}": ds.value("shares_diluted", cur),
                f"shares_diluted@{prev}": ds.value("shares_diluted", prev),
                f"eps_diluted@{cur}": ds.value("eps_diluted", cur),
                f"eps_diluted@{prev}": ds.value("eps_diluted", prev)}
        row = {"period": f"{prev}->{cur}", "inputs": list(need)}
        missing = [k for k, v in need.items() if v is None]
        if missing:
            rows.append(row | {"status": "blocked", "reason": f"missing {', '.join(missing)}"})
            continue
        sh_c, sh_p = need[f"shares_diluted@{cur}"], need[f"shares_diluted@{prev}"]
        eps_c, eps_p = need[f"eps_diluted@{cur}"], need[f"eps_diluted@{prev}"]
        if min(ni_c, ni_p, eps_c, eps_p) <= 0:
            rows.append(row | {"status": "not-applicable",
                               "reason": "growth factors need positive earnings in both years; "
                                         f"EPS changed by {eps_c - eps_p:+.2f} per share"})
            continue

        ni_f, sh_f, eps_f = ni_c / ni_p, sh_c / sh_p, eps_c / eps_p
        implied = ni_f / sh_f
        recomputed = ni_c / sh_c
        gap = eps_c - recomputed
        buybacks, sbc = ds.value("buybacks", cur), ds.value("sbc", cur)
        retired = sh_p - sh_c
        row |= {
            "status": "ok",
            "method": "approximation",
            "numerator": num_name_c,
            "net_income_factor": ni_f,
            "share_factor": sh_f,
            "implied_eps_factor": implied,
            "reported_eps_factor": eps_f,
            "from_earnings_log": math.log(ni_f),
            "from_share_count_log": -math.log(sh_f),
            "residual_log": math.log(eps_f) - math.log(implied),
            "recomputed_eps": recomputed,
            "eps_recompute_gap": gap,
            "eps_recompute_flag": None if abs(gap) <= RECOMPUTE_TOLERANCE else
                f"Reported diluted EPS {eps_c:.2f} vs net income / diluted shares {recomputed:.2f}: "
                "check the diluted numerator (two-class method, participating securities) before relying on the bridge",
            "buybacks": buybacks,
            "sbc": sbc,
            "net_diluted_shares_retired": retired,
            "buyback_note": (
                "Share reduction is not free: it cost the buyback cash shown, part of which offsets "
                "shares issued as stock compensation"
            ),
        }
        rows.append(row)
    return rows
