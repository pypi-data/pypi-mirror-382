__all__ = [
    "dshell_keyword",
    "dshell_discord_keyword",
    "dshell_commands",
    "dshell_mathematical_operators",
    "dshell_logical_operators",
    "dshell_operators",
    "dshell_logical_word_operators"
]

from typing import Callable

from ..DISCORD_COMMANDS.dshell_channel import *
from ..DISCORD_COMMANDS.dshell_member import *
from ..DISCORD_COMMANDS.dshell_message import *
from ..DISCORD_COMMANDS.dshell_pastbin import *
from ..DISCORD_COMMANDS.dshell_role import *
from ..DISCORD_COMMANDS.dshell_interaction import *
from ..DISCORD_COMMANDS.utils.utils_global import *
from ..DISCORD_COMMANDS.utils.utils_list import *
from ..DISCORD_COMMANDS.utils.utils_member import *
from ..DISCORD_COMMANDS.utils.utils_string import *

dshell_keyword: set[str] = {
    'if', 'else', 'elif', 'loop', '#end', 'var', '#loop', '#if', 'sleep', 'param', '#param'
}

dshell_discord_keyword: set[str] = {
    'embed', '#embed', 'field', 'perm', 'permission', '#perm', '#permission', 'ui', '#ui', 'button', 'select'
}
dshell_commands: dict[str, Callable] = {

    ## global utils
    'random': utils_random,

    ## List utils
    'length': utils_len,
    'len': utils_len,
    'add': utils_list_add,
    'remove': utils_list_remove,
    'clear': utils_list_clear,
    'pop': utils_list_pop,
    'sort': utils_list_sort,
    'reverse': utils_list_reverse,
    'get': utils_list_get_value,

    ## String utils
    'split': utils_split_string,
    'upper': utils_upper_string,
    'lower': utils_lower_string,
    'title': utils_title_string,
    'strip': utils_strip_string,
    'replace': utils_replace_string,
    'regex_findall': utils_regex_findall,
    'regex_sub': utils_regex_sub,
    'regex': utils_regex_search,

    ## Discord utils
    'name': utils_get_name, # get the name from id (channel, role, member)
    'id': utils_get_id, # get the id from name (channel, role, member)
    'roles': utils_get_roles, # get all roles of a member

    ## Member utils
    'has_perms': utils_has_permissions, # check if a member has the specified permissions

    ## Pastbin command
    "gp": dshell_get_pastbin,  # get pastbin

    ## Discord commands
    "sm": dshell_send_message,  # send message
    "spm": dshell_send_private_message,  # send private message
    "srm": dshell_respond_message,  # respond to a message
    "dm": dshell_delete_message,
    "pm": dshell_purge_message,
    "em": dshell_edit_message,  # edit message
    "mh": dshell_get_history_messages,  # get message history
    "gcm": dshell_get_content_message,  # get content of a message

    "sri": dshell_respond_interaction,  # respond to an interaction
    "sdi": dshell_defer_interaction,  # defer an interaction
    "dom": dshell_delete_original_message,  # delete original interaction message

    "cc": dshell_create_text_channel,  # create channel
    "cvc": dshell_create_voice_channel,  # create voice channel
    "cca": dshell_create_category,  # create category
    "dc": dshell_delete_channel,  # delete channel
    "dcs": dshell_delete_channels,  # delete several channels by name or regex

    "gc": dshell_get_channel,  # get channel
    "gcs": dshell_get_channels,  # get channels by name or regex
    "gccs": dshell_get_channels_in_category,  # get channels in category

    "ct": dshell_create_thread_message,  # create thread
    "dt": dshell_delete_thread,  # delete thread
    "gt": dshell_get_thread,  # get thread
    "et": dshell_edit_thread,  # edit thread

    "bm": dshell_ban_member,  # ban member
    "um": dshell_unban_member,  # unban member
    "km": dshell_kick_member,  # kick member
    "tm": dshell_timeout_member,  # timeout member
    "mm": dshell_move_member,  # move member to another channel
    "rm": dshell_rename_member,  # rename member
    "cp": dshell_check_permissions,  # check permissions
    "gmr": dshell_give_member_roles, # give roles
    "rmr": dshell_remove_member_roles, # remove roles

    "ec": dshell_edit_text_channel,  # edit text channel
    "evc": dshell_edit_voice_channel,  # edit voice channel
    "eca": dshell_edit_category,  # edit category

    "cr": dshell_create_role, # create role
    "dr": dshell_delete_roles, # delete role
    "er": dshell_edit_role, # edit role

    "ar": dshell_add_reactions,  # add reactions to a message
    "rr": dshell_remove_reactions,  # remove reactions from a message
    "cmr": dshell_clear_message_reactions, # clear reactions from a message
    "cor": dshell_clear_one_reactions , # clear one reaction from a message

}

dshell_mathematical_operators: dict[str, tuple[Callable, int]] = {

    r".": (lambda a, b: a.b, 9),
    r"->": (lambda a: a.at, 10),  # equivalent to calling .at(key)

    r"+": (lambda a, b: a + b, 6),
    r"-": (lambda a, b=None: -a if b is None else a - b, 6),
    # warning: ambiguity between unary and binary to be handled in your parser
    r"**": (lambda a, b: a ** b, 8),
    r"*": (lambda a, b: a * b, 7),
    r"%": (lambda a, b: a % b, 7),
    r"//": (lambda a, b: a // b, 7),
    r"/": (lambda a, b: a / b, 7),
}

dshell_logical_word_operators: dict[str, tuple[Callable, int]] = {
    r"and": (lambda a, b: bool(a and b), 2),
    r"or": (lambda a, b: bool(a or b), 1),
    r"not": (lambda a: not a, 3),
    r"in": (lambda a, b: a in b, 4),
}

dshell_logical_operators: dict[str, tuple[Callable, int]] = {

    r"<": (lambda a, b: a < b, 4),
    r"<=": (lambda a, b: a <= b, 4),
    r"=<": (lambda a, b: a <= b, 4),
    r"=": (lambda a, b: a == b, 4),
    r"!=": (lambda a, b: a != b, 4),
    r"=!": (lambda a, b: a != b, 4),
    r">": (lambda a, b: a > b, 4),
    r">=": (lambda a, b: a >= b, 4),
    r"=>": (lambda a, b: a >= b, 4),
    r"&": (lambda a, b: a & b, 2),
    r"|": (lambda a, b: a | b, 1),

}

dshell_operators: dict[str, tuple[Callable, int]] = dshell_logical_operators.copy()
dshell_operators.update(dshell_logical_word_operators)
dshell_operators.update(dshell_mathematical_operators)

'''
C_create_var = "var"
    C_obligate_var = "ovar" # makes variables mandatory

    # guild
    C_create_channel = "cc"
    C_create_voice_channel = "cvc"
    C_create_forum_channel = "cfc"
    C_create_category = "cca"
    C_create_role = "cr"

    C_delete_channel = "dc"
    C_delete_category = "dca"
    C_delete_role = "dr"

    C_edit_channel = "ec"
    C_edit_voice_channel = "evc"
    C_edit_forum_channel = "efc"
    C_edit_category = "eca"
    C_edit_role = "er"
    C_edit_guild = "eg"

    # forum
    C_edit_ForumTag = "eft"
    C_create_thread = "ct"
    C_delete_tread = "dt"

    # member
    C_edit_nickname = "en"
    C_ban_member = "bm"
    C_unban_member = "um"
    C_kick_member = "km"
    C_timeout_member = "tm"
    C_move_member = "mm"
    C_add_roles = "ar"
    C_remove_roles = "rr"

    # message
    C_send_message = "sm"
    C_respond_message = "rm"
    C_edit_message = "em"
    C_send_user_message = "sum"
    C_delete_message = "dm"
    C_purge_message = "pm"
    C_create_embed = "e"
    C_regex = "regex"
    C_add_emoji = "ae"
    C_remove_emoji = "re"
    C_clear_emoji = "ce"
    C_remove_reaction = "rre"

    # button
    C_create_button = "b"'''
