from __future__ import annotations

import re

import numpy as np


def find_miles(s: str) -> int | None:
    kstyles = ["k", r",*[0-9]+"]
    for kstyle in kstyles:
        thznd = r"\b[0-9]+"
        expressions = [
            r"(" + thznd + kstyle + r") miles",
            r"(" + thznd + kstyle + r") mi",
            r"odometer: (" + thznd + kstyle + r")",
            r"miles: (" + thznd + kstyle + r")",
            r"mileage: (" + thznd + kstyle + r")",
            r"mileage.{0,4}?(" + thznd + kstyle + r")",
            r"miles.{0,4}?(" + thznd + kstyle + r")",
            r"(" + thznd + kstyle + r").{0,4}?miles",
        ]
        for expression in expressions:
            result = re.search(expression, s, flags=re.IGNORECASE)
            if result:
                if kstyle == "k":
                    val = 1000 * int(result.group(1).lower().replace("k", ""))
                else:
                    val = int(result.group(1).replace(",", ""))
                if val < 999_999:
                    return val
    return None


def find_year(s: str) -> int | None:
    # Matches model years 1980–2029; update upper bound as needed
    result = re.search(r"\b(19[89]\d|200\d|201\d|202\d)\b", s)
    if result:
        return int(result.group(1))
    return None


def find_model(s: str, models: set) -> str | None:
    for word in s.lower().split():
        if word in models:
            return word
    return None


def find_phone(s: str) -> str | None:
    for pattern in [r"\d{3}-\d{4}", r"\d{3}\.\d{3}\.\d{4}", r"\d{10}"]:
        result = re.search(pattern, s)
        if result:
            return result.group(0)
    return None


def get_xval_indices(n: int, training_frac: float = 0.8) -> tuple:
    training_n = round(training_frac * n)
    indices = np.random.permutation(range(n))
    return indices[:training_n], indices[training_n:]
