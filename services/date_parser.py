from datetime import date, datetime


def parse_transaction_date(raw_date: str | None) -> datetime:
    if not raw_date:
        return datetime.combine(date.today(), datetime.min.time())

    parts = raw_date.split('.')
    now = datetime.now()

    if len(parts) == 1:
        day = int(parts[0])
        return datetime(now.year, now.month, day)

    if len(parts) == 2:
        day, month = map(int, parts)
        return datetime(now.year, month, day)

    if len(parts) == 3:
        day, month, year = map(int, parts)
        return datetime(year, month, day)

    raise ValueError('Неверный формат даты')


def format_transaction_date(raw_date: str | None) -> str:
    return parse_transaction_date(raw_date).strftime('%d.%m.%Y')
