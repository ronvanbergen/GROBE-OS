import re
from pathlib import Path
from typing import Any, Dict, List
from pypdf import PdfReader

MONEY_RE = re.compile(r"(?:€\s*)?(-?\d{1,3}(?:[\.\s]\d{3})*(?:,\d{2})|-?\d+(?:,\d{2}))")
QTY_RE = re.compile(r"(?<![\d,\.])(-?\d+(?:[\.,]\d{1,3})?)(?![\d,\.])")


def pdf_to_text(path: Path) -> str:
    reader = PdfReader(str(path))
    parts: List[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def parse_decimal(value: str) -> float:
    value = value.strip().replace(" ", "")
    if "," in value:
        value = value.replace(".", "").replace(",", ".")
    return float(value)


def detect_supplier(text: str) -> str:
    upper = text.upper()
    if "JULIUS" in upper or "HOESCH" in upper:
        return "Julius Hoesch"
    if "DISTRIFILL" in upper:
        return "Distrifill"
    if "SUPERDOOS" in upper:
        return "Superdoos"
    return "Onbekend"


def match_invoice_lines(text: str, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    article_map = {a["legacy_number"].upper(): a for a in articles if a.get("legacy_number")}

    for line in lines:
        upper = line.upper()
        matched_key = None
        for legacy in sorted(article_map.keys(), key=len, reverse=True):
            if legacy and legacy in upper:
                matched_key = legacy
                break
        if not matched_key:
            continue

        numbers = MONEY_RE.findall(line)
        decimals = []
        for number in numbers:
            try:
                decimals.append(parse_decimal(number))
            except ValueError:
                pass

        # Simpele eerste aanpak: laatste geldbedrag = totaal of stuksprijs, eerste getal = hoeveelheid.
        qty_candidates = QTY_RE.findall(line)
        quantity = 0.0
        for candidate in qty_candidates:
            try:
                value = parse_decimal(candidate)
                if value > 0:
                    quantity = value
                    break
            except ValueError:
                continue

        unit_price = decimals[-1] if decimals else 0.0
        results.append({
            "legacy_number": matched_key,
            "article_name": article_map[matched_key].get("name", matched_key),
            "raw_line": line,
            "quantity": quantity,
            "unit_price": unit_price,
            "confidence": "basis-herkenning"
        })
    return results
