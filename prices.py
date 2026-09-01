import json
import re
import subprocess
from datetime import datetime
from html import unescape
from zoneinfo import ZoneInfo

try:
    import jdatetime
except ImportError:
    jdatetime = None


TGJU_URL = "https://call5.tgju.org/ajax.json"
TGJU_GOLD_OUNCE_URL = "https://gem.tgju.org/profile/forex-xau-usd"

NOBITEX_URL = (
    "https://apiv2.nobitex.ir/market/stats"
    "?srcCurrency={}&dstCurrency=rls"
)


# =========================================================
# HTTP
# =========================================================

def fetch_json(url):
    result = subprocess.run(
        [
            "curl",
            "-4",
            "-s",
            "--connect-timeout",
            "15",
            url,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or "خطا در اتصال به منبع داده"
        )

    if not result.stdout.strip():
        raise RuntimeError("پاسخ خالی از منبع داده دریافت شد")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"پاسخ JSON معتبر نیست: {exc}"
        ) from exc


def fetch_text(url):
    result = subprocess.run(
        [
            "curl",
            "-4",
            "-L",
            "-s",
            "--connect-timeout",
            "15",
            url,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or "خطا در دریافت صفحه"
        )

    if not result.stdout.strip():
        raise RuntimeError("صفحه خالی دریافت شد")

    return result.stdout


# =========================================================
# NUMBER HELPERS
# =========================================================

def clean_price(value):
    if value is None:
        return None

    try:
        return float(
            str(value)
            .replace(",", "")
            .replace(" ", "")
            .strip()
        )
    except (ValueError, TypeError):
        return None


def rial_to_toman(value):
    price = clean_price(value)

    if price is None:
        return None

    return round(price / 10)


def format_number(value):
    if value is None:
        return "—"

    return f"{int(round(value)):,}"


def format_usd(value):
    if value is None:
        return "—"

    return f"{value:,.2f}"


# =========================================================
# CHANGE
# =========================================================

def get_change_dot(value):
    try:
        change = float(value or 0)
    except (ValueError, TypeError):
        change = 0.0

    if change > 0:
        return "🟢", f"+{change:.2f}%"

    if change < 0:
        return "🔴", f"{change:.2f}%"

    return "⚪", "0.00%"


def get_crypto_change(value):
    try:
        change = float(value or 0)
    except (ValueError, TypeError):
        change = 0.0

    if change > 0:
        return "🟢", "↑", f"+{change:.2f}%"

    if change < 0:
        return "🔴", "↓", f"{change:.2f}%"

    return "⚪", "", "0.00%"


# =========================================================
# TGJU
# =========================================================

def get_tgju():
    data = fetch_json(TGJU_URL)
    return data.get("current", {})


def tgju_item(data, key):
    item = data.get(key)

    if not item:
        return None

    return {
        "price": rial_to_toman(item.get("p")),
        "change_percent": float(item.get("dp") or 0),
    }


# =========================================================
# GOLD OUNCE - TGJU
# =========================================================

def get_gold_ounce():
    html = fetch_text(TGJU_GOLD_OUNCE_URL)

    text = unescape(html)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    price = None

    patterns = [
        r"نرخ فعلی\s*:?\s*:?\s*([0-9][0-9,]*\.[0-9]+)",
        r"نرخ فعلی\s*([0-9][0-9,]*\.[0-9]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            price = clean_price(match.group(1))
            break

    if price is None:
        return None

    change = 0.0

    change_patterns = [
        r"درصد تغییر نسبت به روز گذشته\s*:?\s*([+-]?[0-9]+(?:\.[0-9]+)?)%",
        r"درصد تغییر نسبت به روز گذشته\s*([+-]?[0-9]+(?:\.[0-9]+)?)%",
    ]

    for pattern in change_patterns:
        match = re.search(pattern, text)

        if match:
            change = float(match.group(1))
            break

    return {
        "price": price,
        "change_percent": change,
    }


# =========================================================
# NOBITEX
# =========================================================

def get_nobitex(symbol):
    url = NOBITEX_URL.format(symbol)

    data = fetch_json(url)

    item = data.get("stats", {}).get(f"{symbol}-rls")

    if not item:
        return None

    return {
        "price": rial_to_toman(item.get("latest")),
        "buy": rial_to_toman(item.get("bestBuy")),
        "sell": rial_to_toman(item.get("bestSell")),
        "change_percent": float(item.get("dayChange") or 0),
    }


# =========================================================
# TETHER
# =========================================================

def get_tether():
    data = fetch_json(
        NOBITEX_URL.format("usdt")
    )

    item = data.get("stats", {}).get("usdt-rls")

    if not item:
        return None

    return {
        "price": rial_to_toman(item.get("latest")),
        "buy": rial_to_toman(item.get("bestBuy")),
        "sell": rial_to_toman(item.get("bestSell")),
        "change_percent": float(item.get("dayChange") or 0),
    }


# =========================================================
# GET ALL PRICES
# =========================================================

def get_prices():

    tgju = get_tgju()

    prices = {}

    # Tether
    prices["Tether"] = get_tether()

    # Currencies
    prices["دلار آزاد"] = tgju_item(tgju, "price_dollar_rl")
    prices["یورو"] = tgju_item(tgju, "price_eur")
    prices["درهم"] = tgju_item(tgju, "price_aed")
    prices["لیر ترکیه"] = tgju_item(tgju, "price_try")
    prices["یوان چین"] = tgju_item(tgju, "price_cny")
    prices["پوند انگلیس"] = tgju_item(tgju, "price_gbp")
    prices["دلار کانادا"] = tgju_item(tgju, "price_cad")
    prices["دلار استرالیا"] = tgju_item(tgju, "price_aud")

    # 100 Iraqi Dinar
    iraq = tgju.get("price_iqd")

    if iraq:
        raw_iqd = clean_price(iraq.get("p"))

        prices["۱۰۰ دینار عراق"] = {
            "price": (
                round(raw_iqd * 100)
                if raw_iqd is not None
                else None
            ),
            "change_percent": float(iraq.get("dp") or 0),
        }
    else:
        prices["۱۰۰ دینار عراق"] = None

    # Afghan Afghani
    prices["افغانی"] = tgju_item(tgju, "price_afn")

    # Gold
    prices["گرم طلا ۱۸ عیار"] = tgju_item(tgju, "geram18")
    prices["گرم طلا ۲۴ عیار"] = tgju_item(tgju, "geram24")
    prices["انس جهانی طلا"] = get_gold_ounce()

    # Coins
    prices["سکه امامی"] = tgju_item(tgju, "sekee")
    prices["سکه بهار آزادی"] = tgju_item(tgju, "sekeb")
    prices["نیم‌سکه"] = tgju_item(tgju, "nim")
    prices["ربع‌سکه"] = tgju_item(tgju, "rob")
    prices["سکه گرمی"] = tgju_item(tgju, "gerami")

    # Crypto
    prices["Bitcoin"] = get_nobitex("btc")
    prices["Ethereum"] = get_nobitex("eth")
    prices["BNB"] = get_nobitex("bnb")
    prices["Solana"] = get_nobitex("sol")
    prices["XRP"] = get_nobitex("xrp")
    prices["Dogecoin"] = get_nobitex("doge")
    prices["GRAM"] = get_nobitex("gram")

    return prices


# =========================================================
# DATE / TIME - TEHRAN
# =========================================================

def get_jalali_datetime():

    # زمان واقعی تهران، مستقل از ساعت سرور GitHub
    now = datetime.now(
        ZoneInfo("Asia/Tehran")
    )

    if jdatetime:
        jnow = jdatetime.datetime.fromgregorian(
            datetime=now
        )

        date_text = jnow.strftime("%Y/%m/%d")
        time_text = jnow.strftime("%H:%M")
    else:
        date_text = now.strftime("%Y/%m/%d")
        time_text = now.strftime("%H:%M")

    # تبدیل اعداد انگلیسی به فارسی
    persian_digits = str.maketrans(
        "0123456789",
        "۰۱۲۳۴۵۶۷۸۹"
    )

    return (
        date_text.translate(persian_digits),
        time_text.translate(persian_digits)
    )


# =========================================================
# NORMAL REPORT LINE
# =========================================================

def report_line(
    icon,
    name,
    item,
    usd=False
):
    if not item:
        return f"{icon} {name}: —"

    price = item.get("price")
    change = item.get("change_percent", 0)

    if usd:
        price_text = format_usd(price)
    else:
        price_text = format_number(price)

    dot, percent = get_change_dot(change)

    return (
        f"{icon} {name}: "
        f"{price_text} {dot} {percent}"
    )


# =========================================================
# CRYPTO REPORT LINE
# =========================================================

def crypto_line(name, item):

    if not item:
        return f"⚪  {name}: —"

    price = item.get("price")
    change = item.get("change_percent", 0)

    price_text = format_number(price)

    dot, arrow, percent = get_crypto_change(change)

    if arrow:
        return (
            f"{dot}  {name}: "
            f"{price_text} {arrow} {percent}"
        )

    return (
        f"{dot}  {name}: "
        f"{price_text} {percent}"
    )


# =========================================================
# BUILD REPORT
# =========================================================

def build_report():

    prices = get_prices()

    jalali_date, current_time = get_jalali_datetime()

    lines = []

    # Tether
    tether = prices.get("Tether")

    lines.append("<b>💵 تتر (تومان)</b>")
    lines.append("")

    if tether:
        lines.append(
            f"🟢 خرید: {format_number(tether.get('buy'))}"
        )
        lines.append(
            f"🔴 فروش: {format_number(tether.get('sell'))}"
        )
    else:
        lines.append("🟢 خرید: —")
        lines.append("🔴 فروش: —")

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # Currencies
    lines.append("<b>💱 ارزها (تومان)</b>")
    lines.append("")

    lines.append(
        report_line(
            "💵",
            "دلار آزاد",
            prices.get("دلار آزاد")
        )
    )

    lines.append(
        report_line(
            "💶",
            "یورو",
            prices.get("یورو")
        )
    )

    lines.append(
        report_line(
            "🇦🇪",
            "درهم",
            prices.get("درهم")
        )
    )

    lines.append(
        report_line(
            "🇹🇷",
            "لیر ترکیه",
            prices.get("لیر ترکیه")
        )
    )

    lines.append(
        report_line(
            "🇨🇳",
            "یوان چین",
            prices.get("یوان چین")
        )
    )

    lines.append(
        report_line(
            "🇬🇧",
            "پوند انگلیس",
            prices.get("پوند انگلیس")
        )
    )

    lines.append(
        report_line(
            "🇨🇦",
            "دلار کانادا",
            prices.get("دلار کانادا")
        )
    )

    lines.append(
        report_line(
            "🇦🇺",
            "دلار استرالیا",
            prices.get("دلار استرالیا")
        )
    )

    lines.append(
        report_line(
            "🇮🇶",
            "۱۰۰ دینار عراق",
            prices.get("۱۰۰ دینار عراق")
        )
    )

    lines.append(
        report_line(
            "🇦🇫",
            "افغانی",
            prices.get("افغانی")
        )
    )

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # Gold & Coins
    lines.append("<b>🥇 طلا و سکه (تومان)</b>")
    lines.append("")

    lines.append(
        report_line(
            "🥇",
            "گرم طلا ۱۸ عیار",
            prices.get("گرم طلا ۱۸ عیار")
        )
    )

    lines.append(
        report_line(
            "🥇",
            "گرم طلا ۲۴ عیار",
            prices.get("گرم طلا ۲۴ عیار")
        )
    )

    lines.append(
        report_line(
            "🌐",
            "انس جهانی طلا (USD)",
            prices.get("انس جهانی طلا"),
            usd=True
        )
    )

    lines.append(
        report_line(
            "🟡",
            "سکه امامی",
            prices.get("سکه امامی")
        )
    )

    lines.append(
        report_line(
            "🟡",
            "سکه بهار آزادی",
            prices.get("سکه بهار آزادی")
        )
    )

    lines.append(
        report_line(
            "🟡",
            "نیم‌سکه",
            prices.get("نیم‌سکه")
        )
    )

    lines.append(
        report_line(
            "🟡",
            "ربع‌سکه",
            prices.get("ربع‌سکه")
        )
    )

    lines.append(
        report_line(
            "🟡",
            "سکه گرمی",
            prices.get("سکه گرمی")
        )
    )

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # Crypto
    lines.append("<b>💰 ارزهای دیجیتال (تومان)</b>")
    lines.append("")

    lines.append(
        crypto_line(
            "Bitcoin",
            prices.get("Bitcoin")
        )
    )

    lines.append(
        crypto_line(
            "Ethereum",
            prices.get("Ethereum")
        )
    )

    lines.append(
        crypto_line(
            "BNB",
            prices.get("BNB")
        )
    )

    lines.append(
        crypto_line(
            "Solana",
            prices.get("Solana")
        )
    )

    lines.append(
        crypto_line(
            "XRP",
            prices.get("XRP")
        )
    )

    lines.append(
        crypto_line(
            "Dogecoin",
            prices.get("Dogecoin")
        )
    )

    lines.append(
        crypto_line(
            "GRAM",
            prices.get("GRAM")
        )
    )

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # Footer
    lines.append(
        f"🕐 {jalali_date} | {current_time}"
    )

    lines.append("")
    lines.append("@market_radar_ir")

    return "\n".join(lines)


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":
    print(build_report())
