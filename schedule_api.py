"""
This module provides simple functions that help to get schedule by the
given filters.
"""


import requests
import datetime
import json


SCHED_URL = 'http://calc.nuwm.edu.ua:3002/api/sched'
GROUPS_URL = 'http://desk.nuwm.edu.ua/cgi-bin/timetable.cgi'


def to_date_format(date):
    """Convert datetime.date object to API date string fromat."""
    return date.strftime('%d.%m.%y')


def schedule_by_dates(group, sdate, edate):
    """Return dictionary with schedule information using dates."""
    params = {
        'group': group,
        'sdate': sdate,
        'edate': edate,
        'type': 'days',
    }
    resp = json.loads(requests.get(SCHED_URL, params=params).text)

    return resp


def schedule_by_year_and_week(group, year, week):
    """Return dictionary with schedule information using year and week."""
    params = {
        'group': group,
        'week': week,
        'year': year,
        'type': 'days',
    }
    resp = json.loads(requests.get(SCHED_URL, params=params).text)

    return resp


def today_schedule(group):
    """Return dict with today's schedule information."""
    date = to_date_format(datetime.date.today())
    return schedule_by_dates(group, date, date)


def tomorrow_schedule(group):
    """Return dict with tomorrow's schedule information."""
    date = to_date_format(
        datetime.date.today() + datetime.timedelta(days=1))
    return schedule_by_dates(group, date, date)


def week_schedule(group):
    """Return dict with this week schedule information."""
    year, week, _ = datetime.date.today().isocalendar()
    return schedule_by_year_and_week(group, year, week)

def next_week_schedule(group):
    """Return dict with next week schedule information."""
    date = datetime.date.today() + datetime.timedelta(days=7)
    year, week, _ = date.isocalendar()
    return schedule_by_year_and_week(group, year, week)


def subject_lecturers(group):
    """Return dict with this week schedule information."""
    schedule = week_schedule(group)['response']['schedule']
    schedule.extend(next_week_schedule(group)['response']['schedule'])
    subjects = dict()

    for day in schedule:
        for subj in day['subjects']:
            subj_name = subj['subject']
            lecturer = subj['lecturer']
            
            if not (subj_name in subjects):
                if lecturer != '':
                    subjects[subj_name] = [lecturer]
            elif not (lecturer in subjects[subj_name]):
                subjects[subj_name].append(lecturer)

    return subjects


def get_group_suggestions(group_name):
    """Return list of suggested groups.
    
    Function is requesting to the site that don't have open API.
    Because of that there are some constants in request parameters.
    """
    # server can not handle strings with more than 8 characters
    group_name = group_name[:8]
    params = {
        'n': 701,
        'lev': 142,
        'faculty': 0,
        'query': group_name,
    }
    req = requests.get(GROUPS_URL, params=params)

    # if there are no suggestions server returns not a valid JSON
    try:
        response = json.loads(req.text)
        return response['suggestions']
    except ValueError:
        return list()


def is_exist_group(group_name):
    """Return boolean answer"""
    # comare group_name with list of all group names
    if group_name in get_group_suggestions(''):
        return True
    else:
        return False