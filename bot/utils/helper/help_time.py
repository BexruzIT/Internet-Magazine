from datetime import datetime
from zoneinfo import ZoneInfo

MONTHS_RU = {
    "January": "Января",
    "February": "Февраля",
    "March": "Марта",
    "April": "Апреля",
    "May": "Мая",
    "June": "Июня",
    "July": "Июля",
    "August": "Августа",
    "September": "Сентября",
    "October": "Октября",
    "November": "Ноября",
    "December": "Декабря",
}


def time_formatter(date_time: str, pattern: str = '%Y-год %d-%B %H:%M') -> str:
    dt = datetime.fromisoformat(date_time).replace(tzinfo=ZoneInfo("UTC"))
    dt_uzbekistan = dt.astimezone(ZoneInfo("Asia/Tashkent"))
    formatted = dt_uzbekistan.strftime(pattern)
    for en, ru in MONTHS_RU.items():
        formatted = formatted.replace(en, ru)
    return formatted


def format_price(value) -> str:
    try:
        return f"{float(value):,.0f} so‘m"
    except (ValueError, TypeError):
        return "Noma’lum"
