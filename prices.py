# -*- coding: utf-8 -*-

import json
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo


TGJU_URL = "https://call5.tgju.org/ajax.json"
NOBITEX_URL = "https://apiv2.nobitex.ir/market/stats"

TEHRAN_TZ = ZoneInfo("Asia/Tehran")


# =========================================================
# دریافت JSON
# =========================================================

def fetch_json(url, timeout=20):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Cache-Control": "no-cache",
        },
    )

    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = response.read().decode("utf-8")

    return json.loads(data)


# =========================================================
# تبدیل مقدار به عدد
# =========================================================

def to_number(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()

    text = (
        text.replace(",", "")
        .replace("٬", "")
        .replace("٫", ".")
    )

    try:
        return float(text)
    except (ValueError, TypeError):
        return None


# =========================================================
# ریال به تومان
# =========================================================

def rial_to_toman(value):
    value = to_number(value)

    if value is None:
        return None

    return round(value / 10)


# =========================================================
# دریافت TGJU
# =========================================================

def fetch_tgju():
    data = fetch_json(TGJU_URL)

    if not isinstance(data, dict):
        raise RuntimeError("پاسخ TGJU معتبر نیست.")

    current = data.get("current")

    if not isinstance(current, dict):
        raise RuntimeError(
            "بخش current در پاسخ TGJU پیدا نشد."
        )

    return current


# =========================================================
# دریافت Nobitex
# =========================================================

def fetch_nobitex():
    data = fetch_json(NOBITEX_URL)

    if not isinstance(data, dict):
        raise RuntimeError("پاسخ Nobitex معتبر نیست.")

    stats = data.get("stats")

    if not isinstance(stats, dict):
        raise RuntimeError(
            "بخش stats در پاسخ Nobitex پیدا نشد."
        )

    return stats


# =========================================================
# پیدا کردن اولین کلید معتبر
# =========================================================

def find_first_item(current, keys):
    for key in keys:
        item = current.get(key)

        if isinstance(item, dict) and item.get("p") is not None:
            return key, item

    return None, None


# =========================================================
# ساخت قیمت از TGJU
# =========================================================

def make_from_keys(current, keys):
    key, item = find_first_item(current, keys)

    if not item:
        return {
            "price": None,
            "change_percent": None,
            "source_key": None,
        }

    return {
        "price": rial_to_toman(item.get("p")),
        "change_percent": to_number(item.get("dp")),
        "source_key": key,
    }


# =========================================================
# ارزها
# =========================================================

CURRENCIES = {
    "دلار آزاد": [
        "price_dollar_rl",
        "price_dollar_dt",
    ],

    "یورو": [
        "price_eur",
        "price_eur_rl",
        "price_euro_rl",
        "eur_irr",
    ],

    "درهم": [
        "price_aed_rl",
        "price_aed",
        "aed_irr",
    ],

    "لیر ترکیه": [
        "price_try_rl",
        "price_try",
        "try_irr",
    ],

    "یوان چین": [
        "price_cny_rl",
        "price_cny",
        "cny_irr",
    ],

    "پوند انگلیس": [
        "price_gbp_rl",
        "price_gbp",
        "gbp_irr",
    ],

    "دلار کانادا": [
        "price_cad_rl",
        "price_cad",
        "cad_irr",
    ],

    "دلار استرالیا": [
        "price_aud_rl",
        "price_aud",
        "aud_irr",
    ],

    "دینار عراق": [
        "price_iqd_rl",
        "price_iqd",
        "iqd_irr",
    ],

    "افغانی": [
        "price_afn_rl",
        "price_afn",
        "afghan_irr",
    ],
}


# =========================================================
# طلا و سکه
# =========================================================

def get_gold_and_coins(current):

    result = {}

    # گرم طلای ۱۸ عیار
    result["گرم طلا ۱۸ عیار"] = make_from_keys(
    current,
    [
        "geram18",
    ],
)

    # گرم طلای ۲۴ عیار
    result["گرم طلا ۲۴ عیار"] = make_from_keys(
        current,
        [
            "geram24",
        ],
    )

    # انس جهانی طلا
    ounce_keys = [
        "gold_ounce",
        "ounce_gold",
        "ons",
        "gold_world",
        "gold_world_usd",
        "gold_17_usd",
    ]

    ounce_key, ounce_item = find_first_item(
        current,
        ounce_keys,
    )

    if ounce_item:
        result["انس جهانی طلا (USD)"] = {
            "price": to_number(ounce_item.get("p")),
            "change_percent": to_number(
                ounce_item.get("dp")
            ),
            "source_key": ounce_key,
        }
    else:
        result["انس جهانی طلا (USD)"] = {
            "price": None,
            "change_percent": None,
            "source_key": None,
        }

    # سکه امامی
    result["سکه امامی"] = make_from_keys(
        current,
        [
            "sekee",
            "retail_sekee",
        ],
    )

    # سکه بهار آزادی
    result["سکه بهار آزادی"] = make_from_keys(
        current,
        [
            "sekeb",
            "retail_sekeb",
        ],
    )

    # نیم سکه
    result["نیم‌سکه"] = make_from_keys(
        current,
        [
            "nim",
            "nim_sekee",
            "retail_nim",
            "half_sekee",
        ],
    )

    # ربع سکه
    result["ربع‌سکه"] = make_from_keys(
        current,
        [
            "rob",
            "rob_sekee",
            "retail_rob",
            "quarter_sekee",
        ],
    )

    # سکه گرمی
    result["سکه گرمی"] = make_from_keys(
        current,
        [
            "gerami",
            "retail_gerami",
        ],
    )

    return result


# =========================================================
# ارزهای دیجیتال
# =========================================================

CRYPTO_PAIRS = {
    "Bitcoin": "btc-rls",
    "Ethereum": "eth-rls",
    "BNB": "bnb-rls",
    "Solana": "sol-rls",
    "XRP": "xrp-rls",
    "Dogecoin": "doge-rls",
    "GRAM": "gram-rls",
}


def get_crypto_data(stats):

    result = {}

    for name, pair in CRYPTO_PAIRS.items():

        item = stats.get(pair)

        if not isinstance(item, dict):
            result[name] = None
            continue

        price_raw = item.get("latest")

        if price_raw is None:
            price_raw = item.get("latestTradePrice")

        if price_raw is None:
            price_raw = item.get("latest_trade_price")

        change_raw = item.get("dayChange")

        if change_raw is None:
            change_raw = item.get("day_change")

        result[name] = {
            "price": rial_to_toman(price_raw),
            "change_percent": to_number(change_raw),
            "source_pair": pair,
        }

    return result


# =========================================================
# تتر
# =========================================================

def get_tether(stats):

    item = stats.get("usdt-rls")

    if not isinstance(item, dict):
        return {
            "buy": None,
            "sell": None,
        }

    buy = item.get("bestBuy")

    if buy is None:
        buy = item.get("best_buy")

    sell = item.get("bestSell")

    if sell is None:
        sell = item.get("best_sell")

    return {
        "buy": rial_to_toman(buy),
        "sell": rial_to_toman(sell),
    }


# =========================================================
# دینار عراق
# =========================================================

def get_iraqi_dinar(current):

    keys = [
        "price_iqd_rl",
        "price_iqd",
        "iqd_irr",
    ]

    key, item = find_first_item(current, keys)

    if not item:
        return {
            "price": None,
            "change_percent": None,
            "source_key": None,
        }

    raw_price = to_number(item.get("p"))

    if raw_price is None:
        price = None
    else:
        # قیمت منبع برای 100 دینار است:
        # ریال -> تومان و سپس تقسیم بر 100
        price = raw_price / 1000

    return {
        "price": price,
        "change_percent": to_number(item.get("dp")),
        "source_key": key,
    }

    raw_price = to_number(item.get("p"))

    if raw_price is None:
        price = None
    else:
        # TGJU این مقدار را برای 100 دینار عراق می‌دهد.
        # تبدیل ریال به تومان + تقسیم بر 100
        # نتیجه = قیمت یک دینار عراق
        price = round(raw_price / 1000, 2)

    return {
        "price": price,
        "change_percent": to_number(item.get("dp")),
        "source_key": source_key,
    }


# =========================================================
# دریافت همه قیمت‌ها
# =========================================================

def get_prices():

    current = fetch_tgju()
    stats = fetch_nobitex()

    prices = {}

    # تتر
    prices["تتر"] = get_tether(stats)

    # ارزها
    for name, keys in CURRENCIES.items():

        if name == "دینار عراق":
            prices[name] = get_iraqi_dinar(current)
        else:
            prices[name] = make_from_keys(
                current,
                keys,
            )

    # طلا و سکه
    prices.update(
        get_gold_and_coins(current)
    )

    # کریپتو
    prices.update(
        get_crypto_data(stats)
    )

    return prices


# =========================================================
# فرمت قیمت
# =========================================================

def format_price(value):

    if value is None:
        return "—"

    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.2f}"

    return f"{int(round(value)):,}"


# =========================================================
# فرمت انس
# =========================================================

def format_ounce(value):

    if value is None:
        return "—"

    return f"{value:,.2f}"


# =========================================================
# درصد معمولی
# =========================================================

def format_normal_change(change):

    if change is None:
        return "⚪ 0.00%"

    if change > 0:
        return f"🟢 +{change:.2f}%"

    if change < 0:
        return f"🔴 {change:.2f}%"

    return "⚪ 0.00%"


# =========================================================
# درصد کریپتو
# =========================================================

def format_crypto_change(change):

    if change is None:
        return "⚪ → —"

    if change > 0:
        return f"🟢 ↑ +{change:.2f}%"

    if change < 0:
        return f"🔴 ↓ {change:.2f}%"

    return "⚪ → 0.00%"


# =========================================================
# تبدیل میلادی به شمسی - نسخه صحیح
# =========================================================

def gregorian_to_jalali(gy, gm, gd):

    g_days_in_month = [
        31, 28, 31, 30, 31, 30,
        31, 31, 30, 31, 30, 31
    ]

    gy2 = gy - 1600
    gm2 = gm - 1
    gd2 = gd - 1

    g_day_no = (
        365 * gy2
        + (gy2 + 3) // 4
        - (gy2 + 99) // 100
        + (gy2 + 399) // 400
    )

    for i in range(gm2):
        g_day_no += g_days_in_month[i]

    if (
        gm2 > 1
        and (
            gy % 4 == 0
            and (
                gy % 100 != 0
                or gy % 400 == 0
            )
        )
    ):
        g_day_no += 1

    g_day_no += gd2

    j_day_no = g_day_no - 79

    j_np = j_day_no // 12053
    j_day_no %= 12053

    jy = (
        979
        + 33 * j_np
        + 4 * (j_day_no // 1461)
    )

    j_day_no %= 1461

    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365

    if j_day_no < 186:
        jm = 1 + j_day_no // 31
        jd = 1 + j_day_no % 31
    else:
        jm = 7 + (j_day_no - 186) // 30
        jd = 1 + (j_day_no - 186) % 30

    return jy, jm, jd

# =========================================================
# اعداد فارسی
# =========================================================

def persian_digits(value):

    return str(value).translate(
        str.maketrans(
            "0123456789",
            "۰۱۲۳۴۵۶۷۸۹",
        )
    )


# =========================================================
# ساعت تهران
# =========================================================

def get_tehran_datetime():

    return datetime.now(TEHRAN_TZ)


def get_persian_datetime():

    now = get_tehran_datetime()

    jy, jm, jd = gregorian_to_jalali(
        now.year,
        now.month,
        now.day,
    )

    date_text = (
        f"{jy:04d}/{jm:02d}/{jd:02d}"
    )

    time_text = (
        f"{now.hour:02d}:{now.minute:02d}"
    )

    return (
        persian_digits(date_text),
        persian_digits(time_text),
    )


# =========================================================
# ساخت گزارش
# =========================================================

def build_report():

    p = get_prices()

    date_text, time_text = get_persian_datetime()

    lines = []

    # =====================================================
    # تتر
    # =====================================================

    lines.append("<b>💵 تتر (تومان)</b>")
    lines.append("")

    tether = p.get("تتر", {})

    lines.append(
        f"🟢 خرید: {format_price(tether.get('buy'))}"
    )

    lines.append(
        f"🔴 فروش: {format_price(tether.get('sell'))}"
    )

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # =====================================================
    # ارزها
    # =====================================================

    lines.append("<b>💱 ارزها (تومان)</b>")
    lines.append("")

    currency_icons = {
        "دلار آزاد": "💵",
        "یورو": "💶",
        "درهم": "🇦🇪",
        "لیر ترکیه": "🇹🇷",
        "یوان چین": "🇨🇳",
        "پوند انگلیس": "🇬🇧",
        "دلار کانادا": "🇨🇦",
        "دلار استرالیا": "🇦🇺",
        "دینار عراق": "🇮🇶",
        "افغانی": "🇦🇫",
    }

    for name in CURRENCIES:

        item = p.get(name, {})

        icon = currency_icons.get(
            name,
            "💱",
        )

        price = item.get("price")
        change = item.get("change_percent")

        lines.append(
            f"{icon} {name}: "
            f"{format_price(price)} "
            f"{format_normal_change(change)}"
        )

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # =====================================================
    # طلا و سکه
    # =====================================================

    lines.append(
        "<b>🥇 طلا و سکه (تومان)</b>"
    )

    lines.append("")

    gold_items = [
        ("🥇", "گرم طلا ۱۸ عیار"),
        ("🥇", "گرم طلا ۲۴ عیار"),
        ("🌐", "انس جهانی طلا (USD)"),
        ("🟡", "سکه امامی"),
        ("🟡", "سکه بهار آزادی"),
        ("🟡", "نیم‌سکه"),
        ("🟡", "ربع‌سکه"),
        ("🟡", "سکه گرمی"),
    ]

    for icon, name in gold_items:

        item = p.get(name, {})

        price = item.get("price")
        change = item.get("change_percent")

        if name == "انس جهانی طلا (USD)":
            price_text = format_ounce(price)
        else:
            price_text = format_price(price)

        lines.append(
            f"{icon} {name}: "
            f"{price_text} "
            f"{format_normal_change(change)}"
        )

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # =====================================================
    # کریپتو
    # =====================================================

    lines.append(
        "<b>💰 ارزهای دیجیتال (تومان)</b>"
    )

    lines.append("")

    for name in CRYPTO_PAIRS:

        item = p.get(name)

        if not item:
            continue

        price = item.get("price")
        change = item.get("change_percent")

        status = format_crypto_change(change)
        status_parts = status.split()

        lines.append(
            f"{status_parts[0]} "
            f"{name}: "
            f"{format_price(price)} "
            f"{' '.join(status_parts[1:])}"
        )

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # =====================================================
    # تاریخ و ساعت تهران
    # =====================================================

    lines.append(
        f"🕐 {date_text} | {time_text}"
    )

    lines.append("")

    lines.append("@market_radar_ir")

    return "\n".join(lines)