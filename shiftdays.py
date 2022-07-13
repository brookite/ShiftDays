import datetime
import argparse
import dateparser
import calendar
import copy
import locale
from sequences import ArithmethicProgression
from bs4 import BeautifulSoup as bs


locale.setlocale(locale.LC_ALL, '')


def compute_shifts(
    target: datetime.datetime,
    known_date: datetime.datetime,
    delta: int
):
    delta = (delta + 1) * 3600 * 24
    progression = ArithmethicProgression(delta, int(known_date.timestamp()))

    last_monthday = calendar.monthrange(target.year, target.month)[1]
    month_start = datetime.datetime(target.year, target.month, 1)
    month_end = datetime.datetime(target.year, target.month, last_monthday)

    s = progression.find_nearest(int(month_start.timestamp())) - 1
    e = progression.find_nearest(int(month_end.timestamp())) + 1

    dates = []
    for i in range(s, e):
        date = datetime.datetime.fromtimestamp(progression[i])
        if date.month == target.month and date.year == target.year:
            dates.append(date)
    dates.sort()
    return dates


def prettify_message(target_date, dates):
    dates = ", ".join(list(map(lambda x: str(x.day), dates)))
    monthname = get_month_name(target_date.month, target_date.year)
    return f"{monthname}:\n{dates}"


def get_month_name(month, year):
    return datetime.datetime(year, month, 1, tzinfo=None).strftime('%B %Y').capitalize()


def parse_htmltemplate():
    with open("calendar.html", encoding="utf-8") as fobj:
        soup = bs(fobj.read(), "html.parser")
    calendarobject = soup.select(".month")[0]
    soup.select(".container")[0].clear()
    return calendarobject, soup


def form_month(month_calendar, year, month, marked_days):
    month_calendar = copy.deepcopy(month_calendar)
    date = datetime.datetime(year, month, 1)

    first_weekday = date.weekday()
    weekobj = month_calendar.select(".week")[0]
    weektemplate = copy.deepcopy(weekobj)

    index = 0
    while date.month == month:
        for item in weekobj.children:
            if not isinstance(item, str):
                if index >= first_weekday:
                    item.string = str(date.day)
                    if date.day in marked_days:
                        item.attrs["class"] = "marked"
                    date += datetime.timedelta(days=1)
                    if date.month != month:
                        break
                index += 1
                if index % 7 == 0:
                    month_calendar.append(copy.deepcopy(weektemplate))
                    weekobj = month_calendar.contents[-1]
                    break
    month_calendar.select(".header")[0].string = get_month_name(month, year)
    return month_calendar


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Месяц или год который требуется для поиска смен")
    parser.add_argument("knowndate", help="Известная дата любой смены")
    parser.add_argument("delta", type=int, help="Периодичность смены")
    parser.add_argument("--export-html", help="Экспортировать результат в html", action='store_true')
    parser.add_argument("--only-month", help="Вывести только указанный месяц", action='store_true')
    args = parser.parse_args()

    target_date = dateparser.parse(args.target, settings={'TIMEZONE': 'UTC'})
    known_date = dateparser.parse(args.knowndate, settings={'TIMEZONE': 'UTC'})

    if args.only_month:
        dates = compute_shifts(target_date, known_date, args.delta)
        print(prettify_message(target_date, dates))
    else:
        for i in range(1, 12 + 1):
            month_date = datetime.datetime(target_date.year, i, 1)
            dates = compute_shifts(month_date, known_date, 3)
            print(prettify_message(month_date, dates))
            print()
    if args.export_html:
        monthcalendar, soup = parse_htmltemplate()
        for i in range(1, 13):
            month_date = datetime.datetime(target_date.year, i, 1)
            dates = compute_shifts(month_date, known_date, 3)
            month = form_month(monthcalendar, target_date.year, i, list(map(lambda x: int(x.day), dates)))
            soup.select(".container")[0].append(month)
        soup.select(".year-header")[0].string = soup.select(".year-header")[0].string.format(target_date.year)
        with open("export.html", "w", encoding="utf-8") as fobj:
            fobj.write(str(soup))

