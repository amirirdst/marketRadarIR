# -*- coding: utf-8 -*-

import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor


TGJU_URL = "https://call5.tgju.org/ajax.json"
NOBITEX_URL = "https://apiv2.nobitex.ir/market/stats"


# ---------------------------------------------------------
# HTTP
# ---------------------------------------------------------

def fetch_json(url, timeout=10):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read().decode("utf-8")

    return json.loads(data)


def fetch_tgju():
    return fetch_json(TGJU_URL, timeout=10)


def fetch_nobitex():
    return fetch_json(NOBITEX_URL, timeout=10)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def safe_float(value):
    try:
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        value = str(value).replace(",", "").strip()

        if not value:
            return None

        return float(value)

    except (ValueError, TypeError):
        return None


def format_price(value):
    value = safe_float(value)

    if value is None:
        return "نامشخص"

    return f"{value:,.0f}"


def get_tgju_value(current, key):
    item = current.get(key)

    if isinstance(item, dict):
        for field in ("p", "price", "value", "last"):
            if field in item:
                value = safe_float(item[field])
                if value is not None:
                    return value

    return safe_float(item)


def get_nobitex_value(stats, symbol):
    item = stats.get(symbol)

    if not isinstance(item, dict):
        return None

    for field in ("latest", "lastTradePrice", "price"):
        if field in item:
            value = safe_float(item[field])

            if value is not None:
                # Nobitex prices are in Rial.
                return value / 10

    return None


# ---------------------------------------------------------
# TGJU
# ---------------------------------------------------------

def extract_tgju_current(data):
    if not isinstance(data, dict):
        return {}

    current = data.get("current")

    if isinstance(current, dict):
        return current

    return {}


# ---------------------------------------------------------
# Nobitex
# ---------------------------------------------------------

def extract_nobitex_stats(data):
    if not isinstance(data, dict):
        return {}

    stats = data.get("stats")

    if isinstance(stats, dict):
        return stats

    return {}


# ---------------------------------------------------------
# Main price collection
# ---------------------------------------------------------

def get_prices():
    """
    دریافت همزمان TGJU و Nobitex.

    قبلاً منابع پشت سر هم دریافت می‌شدند.
    حالا هر دو درخواست همزمان اجرا می‌شوند تا
    کندی یک منبع باعث معطل شدن منبع دیگر نشود.
    """

    with ThreadPoolExecutor(max_workers=2) as executor:

        tgju_future = executor.submit(fetch_tgju)
        nobitex_future = executor.submit(fetch_nobitex)

        tgju_data = tgju_future.result()
        nobitex_data = nobitex_future.result()

    current = extract_tgju_current(tgju_data)
    stats = extract_nobitex_stats(nobitex_data)

    prices = {}

    # -----------------------------------------------------
    # ارزهای TGJU
    # -----------------------------------------------------

    currency_keys = {
        "دلار آزاد": "price_dollar_rl",
        "یورو": "price_eur",
        "درهم": "price_aed",
        "لیر ترکیه": "price_try",
        "یوان چین": "price_cny",
        "پوند انگلیس": "price_gbp",
        "دلار کانادا": "price_cad",
        "دلار استرالیا": "price_aud",
        "دینار عراق": "price_iqd",
        "افغانی": "price_afn",
    }

    for name, key in currency_keys.items():
        value = get_tgju_value(current, key)

        if value is not None:
            prices[name] = value

    # -----------------------------------------------------
    # طلا
    # -----------------------------------------------------

    gold_18 = get_tgju_value(current, "geram18")
    gold_24 = get_tgju_value(current, "geram24")

    if gold_18 is not None:
        prices["طلای ۱۸ عیار"] = gold_18

    if gold_24 is not None:
        prices["طلای ۲۴ عیار"] = gold_24

    # -----------------------------------------------------
    # سکه
    # -----------------------------------------------------

    coin_keys = {
        "سکه امامی": "sekee",
        "سکه بهار آزادی": "sekeb",
        "نیم‌سکه": "nim",
        "ربع‌سکه": "rob",
        "سکه گرمی": "gerami",
    }

    for name, key in coin_keys.items():
        value = get_tgju_value(current, key)

        if value is not None:
            prices[name] = value

    # -----------------------------------------------------
    # ارزهای دیجیتال از Nobitex
    # -----------------------------------------------------

    crypto_symbols = {
        "تتر": "usdt-rls",
        "بیت‌کوین": "btc-rls",
        "اتریوم": "eth-rls",
        "ریپل": "xrp-rls",
        "BNB": "bnb-rls",
        "دوج‌کوین": "doge-rls",
        "سولانا": "sol-rls",
        "گرام": "gram-rls",
    }

    for name, symbol in crypto_symbols.items():
        value = get_nobitex_value(stats, symbol)

        if value is not None:
            prices[name] = value

    return prices


# ---------------------------------------------------------
# Report
# ---------------------------------------------------------

def build_report():
    prices = get_prices()

    lines = []

    lines.append("📊 <b>رادار بازار</b>")
    lines.append("━━━━━━━━━━━━━━━━━━")

    sections = [
        (
            "💵 ارز",
            [
                "دلار آزاد",
                "یورو",
                "درهم",
                "لیر ترکیه",
                "یوان چین",
                "پوند انگلیس",
                "دلار کانادا",
                "دلار استرالیا",
                "دینار عراق",
                "افغانی",
            ],
        ),
        (
            "🥇 طلا",
            [
                "طلای ۱۸ عیار",
                "طلای ۲۴ عیار",
            ],
        ),
        (
            "🪙 سکه",
            [
                "سکه امامی",
                "سکه بهار آزادی",
                "نیم‌سکه",
                "ربع‌سکه",
                "سکه گرمی",
            ],
        ),
        (
            "₿ کریپتو",
            [
                "تتر",
                "بیت‌کوین",
                "اتریوم",
                "ریپل",
                "BNB",
                "دوج‌کوین",
                "سولانا",
                "گرام",
            ],
        ),
    ]

    for title, items in sections:

        available = [
            item
            for item in items
            if item in prices
        ]

        if not available:
            continue

        lines.append("")
        lines.append(f"<b>{title}</b>")

        for item in available:
            lines.append(
                f"• {item}: "
                f"<b>{format_price(prices[item])}</b> تومان"
            )

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("⏱️ به‌روزرسانی خودکار بازار")

    return "\n".join(lines)


# ---------------------------------------------------------
# Compatibility helpers
# ---------------------------------------------------------

def get_prices_fast():
    """
    نام جایگزین برای استفاده احتمالی در نسخه‌های قبلی پروژه.
    """
    return get_prices()


if __name__ == "__main__":
    print(build_report())
