#!/usr/bin/env python3
"""Offline budget arithmetic. Never submits jobs, fetches prices or authorizes spending."""
import argparse, json, sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

def number(value, label, integer=False):
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(label + " must be numeric, not boolean")
    try:
        v = Decimal(str(value))
    except InvalidOperation:
        raise ValueError(label + " must be numeric")
    if not v.is_finite() or v < 0 or (integer and v != v.to_integral_value()):
        raise ValueError(label + " must be finite, non-negative" + (" integer" if integer else ""))
    return v

def calculate(data):
    if not isinstance(data, dict):
        raise ValueError("budget must be a JSON object")
    if not isinstance(data.get("items"), list) or not data["items"]:
        raise ValueError("items must be a nonempty list")
    missing, lines, subtotal, seen = [], [], Decimal(0), set()
    for index, item in enumerate(data["items"]):
        if not isinstance(item, dict):
            raise ValueError("each item must be a JSON object")
        label = item.get("id") or f"item-{index+1}"
        if label in seen:
            raise ValueError("duplicate item id: " + label)
        seen.add(label)
        q = number(item.get("quantity"), label + ".quantity")
        rate = number(item.get("unit_credits"), label + ".unit_credits")
        attempts = number(item.get("attempts", 1), label + ".attempts", integer=True)
        absent = [k for k,v in (("quantity",q),("unit_credits",rate),("attempts",attempts)) if v is None]
        if absent:
            missing.extend(label+"."+k for k in absent)
            total = None
        else:
            total = q * rate * attempts
            subtotal += total
        lines.append({"id":label,"credits":None if total is None else str(total),
                      "conditional":bool(item.get("conditional",False))})
    reserve = number(data.get("reserve_credits",0),"reserve_credits")
    cap = number(data.get("cap_credits"),"cap_credits")
    if reserve is None:
        missing.append("reserve_credits")
    complete = not missing
    total = subtotal + reserve if complete else None
    return {"status":"COMPLETE_ESTIMATE" if complete else "INCOMPLETE",
            "scope":"Arithmetic only; includes all listed conditional attempts; not an authorization.",
            "lines":lines,"known_items_subtotal":str(subtotal),
            "subtotal_credits":str(subtotal) if complete else None,
            "reserve_credits":None if reserve is None else str(reserve),
            "total_credits":None if total is None else str(total),
            "cap_credits":None if cap is None else str(cap),
            "within_cap":None if total is None or cap is None else total<=cap,
            "missing":missing,"prices_verified_by_tool":False,"jobs_submitted":0}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("budget",type=Path); p.add_argument("--out",type=Path)
    a=p.parse_args()
    try:
        result=calculate(json.loads(a.budget.read_text(encoding="utf-8")))
    except (ValueError,TypeError,KeyError,OSError) as e:
        print(json.dumps({"status":"INVALID","error":str(e)},ensure_ascii=False))
        return 2
    text=json.dumps(result,ensure_ascii=False,indent=2)
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(text+"\n",encoding="utf-8")
    print(text)
    return 1 if result["status"]=="INCOMPLETE" or result["within_cap"] is False else 0

if __name__=="__main__":
    sys.exit(main())
