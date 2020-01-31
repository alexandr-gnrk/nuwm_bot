import os
import logging
from functools import wraps
import telebot

import schedule_api as api
import messages as msgs
from schedule_prettifier import schedule_to_markdown
from schedule_prettifier import subject_lecturers_to_markdown
import orm


TOKEN = os.environ['NUWM_TELEGRAM_BOT_TOKEN']
bot = telebot.TeleBot(TOKEN)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


def extract_arg(arg):
    """Return list of arguments by command string."""
    return arg.split()[1:]


def extract_command(arg):
    """Return command name by command string.
    
    Also handle commands from chats.
    """
    cmd = arg.split()[0][1:]
    # check, is command called from private chat
    if '@' in cmd:
        cmd = cmd.split('@')[0]
    return cmd


def group_is_selected(handler):
    """Requires the user to select the group.

    If group isn't selected, a request is sending.
    """
    @wraps(handler)
    def inner(message):
        user = orm.get_user_by_id(message.from_user.id)
        if (not user) or (user.group_name is None):
            bot.send_message(message.chat.id, msgs.SELECT_GROUP)
            return
        return handler(message)

    return inner


def create_user_if_not_exist(handler):
    """Create user in database if it's not there."""
    @wraps(handler)
    def inner(message):
        user = orm.get_user_by_id(message.from_user.id)
        if not user:
            orm.create_user(message.from_user.id, None)
        return handler(message)

    return inner


@bot.message_handler(commands=['start', 'help', 'timetable'])
def start(message):
    cmd = extract_command(message.text)
    if cmd == 'start':
        msg = msgs.START
    elif cmd == 'help':
        msg = msgs.HELP
    elif cmd == 'timetable':
        msg = msgs.TIMETABLE
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')


@bot.message_handler(
    func=lambda message: message.text in ('/gr', '/gr@vodniks_chedule_bot'))
@create_user_if_not_exist
def get_current_group(message):
    user = orm.get_user_by_id(message.from_user.id)
    
    if user.group_name == None:
        msg = msgs.SELECT_GROUP
    else:
        msg = msgs.SELECTED_GROUP.\
            format(user.group_name)

    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['gr'])
@create_user_if_not_exist
def gr(message):
    args = extract_arg(message.text)
    user = orm.get_user_by_id(message.from_user.id)

    group_name = args[0]
    print(group_name)
    print(len(group_name))

    # send suggestions if recived group name is not exist 
    if not api.is_exist_group(group_name):
        bot.send_message(message.chat.id, msgs.WRONG_GROUP)
        sugg_groups = api.get_group_suggestions(group_name)
        # make string with up to 8 suggested groups 
        if sugg_groups:
            sugg_string = '\n• '.join(sugg_groups[:8])
            bot.send_message(message.chat.id, 
                msgs.SUGGEST_GROUP.format(sugg_string))
        return

    if user.group_name == group_name:
        bot.send_message(message.chat.id, 
            msgs.SAME_GROUP.format(group_name))
        return
    
    bot.send_message(message.chat.id, 
        msgs.CHANGE_GROUP.format(group_name))

    user.group_name = group_name
    orm.session.commit()


@bot.message_handler(commands=['today', 'tomorrow', 'week', 'nextweek'])
@group_is_selected
def show_schedule(message):
    group = orm.get_user_by_id(message.from_user.id).group_name
    cmd = extract_command(message.text)

    methods_map = {
        'today': api.today_schedule,
        'tomorrow': api.tomorrow_schedule,
        'week': api.week_schedule,
        'nextweek': api.next_week_schedule,}

    no_lessons_map = {
        'today': msgs.NO_LESSONS_TODAY,
        'tomorrow': msgs.NO_LESSONS_TOMORROW,
        'week': msgs.NO_LESSONS_WEEK,
        'nextweek': msgs.NO_LESSONS_NEXT_WEEK,
    }

    resp = methods_map[cmd](group)

    if (resp['error'] != 'Not Found') and (resp['error'] is not None):
        msg = msgs.API_SERVER_ERROR
    elif resp['response'] is None:
        msg = no_lessons_map[cmd]
    else:
        msg = schedule_to_markdown(resp['response']['schedule'])

    bot.send_message(message.chat.id, msg, parse_mode='Markdown')


@bot.message_handler(commands=['lecturers', 'teachers'])
@group_is_selected
def show_lecturers(message):
    group = orm.get_user_by_id(message.from_user.id).group_name
    subjects = api.subject_lecturers(group)
    
    if subjects:
        msg = subject_lecturers_to_markdown(subjects)
    else:
        msg = msgs.NO_SCHEDULE

    bot.send_message(message.chat.id, msg, parse_mode='Markdown')


bot.polling(timeout=30)