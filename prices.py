import json
import subprocess
from datetime import datetime

try:
    import jdatetime
except ImportError:
    jdatetime = None


TGJU_URL = "https://call5.tgju.org/ajax.json"

NOBITEX_URL = (
    "https://apiv2.nobitex.ir/market/stats"
    "?srcCurrency={}&dstCurrency=rls"
)


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
            result.stderr.strip() or "خطا در اتصال به سرور"
        )

    if not result.stdout.strip():
        raise RuntimeError("پاسخ خالی از سرور دریافت شد")

    return json.loads(result.stdout)


def clean_price(value):
    if value is None:
        return None

    try:
        return float(
            str(value).replace(",", "").strip()
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


def format_change(value):
    try:
        change = float(value or 0)
    except (ValueError, TypeError):
        change = 0

    if change > 0:
        return f"🟢 +{change:.2f}%"

    if change < 0:
        return f"🔴 {change:.2f}%"

    return "⚪ 0.00%"


# =========================
# TGJU
# =========================

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


# =========================
# NOBITEX
# =========================

def get_nobitex(symbol):
    url = NOBITEX_URL.format(symbol)

    data = fetch_json(url)

    item = data.get("stats", {}).get(
        f"{symbol}-rls"
    )

    if not item:
        return None

    return {
        "price": rial_to_toman(item.get("latest")),
        "buy": rial_to_toman(item.get("bestBuy")),
        "sell": rial_to_toman(item.get("bestSell")),
        "change_percent": float(
            item.get("dayChange") or 0
        ),
    }


# =========================
# قیمت‌ها
# =========================

def get_prices():

    tgju = get_tgju()

    prices = {}

    # ارزها
    prices["دلار آزاد"] = tgju_item(
        tgju, "price_dollar_rl"
    )

    prices["یورو"] = tgju_item(
        tgju, "price_eur"
    )

    prices["درهم"] = tgju_item(
        tgju, "price_aed"
    )

    prices["لیر ترکیه"] = tgju_item(
        tgju, "price_try"
    )

    # طلا و سکه
    prices["طلای ۱۸"] = tgju_item(
        tgju, "tgju_gold_irg18"
    )

    prices["سکه امامی"] = tgju_item(
        tgju, "sekee"
    )

    prices["نیم‌سکه"] = tgju_item(
        tgju, "nim"
    )

    prices["ربع‌سکه"] = tgju_item(
        tgju, "rob"
    )

    prices["سکه گرمی"] = tgju_item(
        tgju, "gerami"
    )

    # نوبیتکس
    for name, symbol in [
        ("تتر", "usdt"),
        ("بیت‌کوین", "btc"),
        ("اتریوم", "eth"),
    ]:
        try:
            prices[name] = get_nobitex(symbol)
        except Exception as error:
            print(f"⚠️ خطای {name}: {error}")
            prices[name] = None

    return prices


# =========================
# ساخت ردیف قیمت
# =========================

def price_row(icon, name, prices):

    item = prices.get(name)

    if not item or item.get("price") is None:
        return f"{icon} {name}: —"

    return (
        f"{icon} {name}: "
        f"{format_number(item['price'])} تومان "
        f"{format_change(item['change_percent'])}"
    )


# =========================
# گزارش
# =========================

def build_report():

    prices = get_prices()

    now = datetime.now()

    # تاریخ شمسی
    if jdatetime:

        jalali = jdatetime.datetime.fromgregorian(
            datetime=now
        )

        date_text = jalali.strftime("%Y/%m/%d")

    else:

        date_text = now.strftime("%Y/%m/%d")

    time_text = now.strftime("%H:%M")

    lines = []

    # =========================
    # تتر
    # =========================

    lines.append("<b>🪙 تتر</b>")
    lines.append("")

    tether = prices.get("تتر")

    if tether:

        lines.append(
            f"🟢 خرید: "
            f"{format_number(tether.get('buy'))} تومان"
        )

        lines.append(
            f"🔴 فروش: "
            f"{format_number(tether.get('sell'))} تومان"
        )

    else:

        lines.append("🟢 خرید: —")
        lines.append("🔴 فروش: —")

    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # =========================
    # ارزها
    # =========================

    lines.append("<b>💱 ارزها</b>")
    lines.append("")

    lines.append(
        price_row("💵", "دلار آزاد", prices)
    )

    lines.append(
        price_row("💶", "یورو", prices)
    )

    lines.append(
        price_row("🇦🇪", "درهم", prices)
    )

    lines.append(
        price_row("🇹🇷", "لیر ترکیه", prices)
    )

    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # =========================
    # طلا و سکه
    # =========================

    lines.append("<b>🥇 طلا و سکه</b>")
    lines.append("")

    lines.append(
        price_row("🥇", "طلای ۱۸", prices)
    )

    lines.append(
        price_row("🪙", "سکه امامی", prices)
    )

    lines.append(
        price_row("🪙", "نیم‌سکه", prices)
    )

    lines.append(
        price_row("🪙", "ربع‌سکه", prices)
    )

    lines.append(
        price_row("🪙", "سکه گرمی", prices)
    )

    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # =========================
    # ارز دیجیتال
    # =========================

    lines.append("<b>₿ ارزهای دیجیتال</b>")
    lines.append("")

    lines.append(
        price_row("₿", "بیت‌کوین", prices)
    )

    lines.append(
        price_row("Ξ", "اتریوم", prices)
    )

    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # =========================
    # تاریخ و ساعت
    # =========================

    lines.append(
        f"🕐 {date_text} | {time_text}"
    )

    lines.append("@market_radar_ir")

    return "\n".join(lines)


if __name__ == "__main__":
    print(build_report())