"""
This module provides functions that are used for convert API response
objects to markdown text.
"""


# this dict helps to shrink subject type names  
SUBJ_TYPE_MAP = {
    'Лекція': 'Лек',
    'Практичне заняття': 'Прак',
    'Консультація': 'Конс',
    'Лабораторна робота': 'Лаб'
}


def schedule_to_markdown(schedule):
    """Return prettified schedule string."""
    text = ''
    for day in schedule:
        text += day_to_markdown(day)
    return text


def to_markdown_safe_text(text):
    """Return string without markdown unsafe characters."""
    return text.\
        replace('`', '\'').\
        replace('*', '#').\
        replace('_', '-')


def day_to_markdown(day):
    """Return prettified day schedule string."""
    dayname = day['dayname']
    day_and_month = day['day'][:5] # '05.11.2020' -> '05.11'
    legend_center = '┫ {} {} ┣'.format(dayname, day_and_month)
    text = '`{:━^27}`\n'.format(legend_center)

    lessons = day['subjects']
    for i in range(len(lessons)):
        # continue print lessons without number and time
        # if there are several lessons at the same time 
        if i - 1 != -1 and \
                lessons[i]['lessonNum'] == lessons[i - 1]['lessonNum']:
            text += lesson_to_markdown(lessons[i], sub_lesson=True)
        else:
            text += lesson_to_markdown(lessons[i])

    text += '\n'
    return text


def lesson_to_markdown(lesson, sub_lesson=False, subj_len=25):
    """Return prettified lesson schedule string.

    Several lessons could be with the same lesson number.
    It means that there are different lessons in different 
    subgroups at the same time.
    
    If function is called with sub_lesson parametr, lesson number
    and schedule time would be added to result string.
    """

    # replace special Markdown characters
    lesson['subject'] = to_markdown_safe_text(lesson['subject'])

    # deleting extra characters in subject name 
    if len(lesson['subject']) > subj_len:
        lesson['subject'] = lesson['subject'][:subj_len - 2] + '..'
    
    # shortering the subject type if it possible
    if lesson['type'] in SUBJ_TYPE_MAP:
        lesson['type'] = SUBJ_TYPE_MAP[lesson['type']]

    # return text without lessonNum and time if it is sub lesson
    if sub_lesson:
        text = '  `│` {} `{}` _{}_\n'.format(
            lesson['subject'],
            lesson['classroom'],
            lesson['type'],)
    else:
        text = '*{})*_{:^50}_\n{}'.format(
            lesson['lessonNum'],
            lesson['time'],
            lesson_to_markdown(
                lesson, 
                sub_lesson=True, 
                subj_len=subj_len))
    return text


def subject_lecturers_to_markdown(subjects):
    """Return string of prettified  lecturers list."""
    text = '`{:━^27}`\n'.format('┫ Твої викладачі ┣')

    for i, (subject, lecturers) in enumerate(subjects.items()):
        subject = to_markdown_safe_text(subject)
        
        # add number and name of subject
        text += '*{})* {}\n'.format(i + 1, subject)

        # add list of lecturers
        for lecturer in lecturers[:-1]:
            text += '`┣` _{}_\n'.format(lecturer)
        text += '`┗` _{}_\n'.format(lecturers[-1])
        text += '\n'

    return text