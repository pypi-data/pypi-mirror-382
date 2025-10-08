"""
Helper functions for colorful output
"""
import logging
import re
import shutil
from enum import Enum

from colorama import Back, Fore, Style

__author__ = 'Sebastian Stigler'
__copyright__ = 'Sebastian Stigler'
__license__ = 'mit'

_logger = logging.getLogger(__name__)


class State(Enum):
    """Enum for States"""
    OK = 1
    FAIL = 2
    NONE = 99


def split_text(text, line_length):
    """Splits the text in lines of a given length

    The split will be on the space character.

    :param text: Text
    :param line_length: Maximal line length
    :yield (line, over, last): where `over` is True if the line is to long
                               and `last` is True on the last line
    """
    remainder = text.strip()
    over = False
    while len(remainder) > line_length:
        idx = remainder.rfind(' ', 0, line_length + 1)
        if idx == -1:  # long word found
            idx = remainder.find(' ')
            over = True
            if idx == -1:  # long word is last word in text
                break
        yield remainder[:idx], over, False
        remainder = remainder[idx:].strip()
        over = False
    yield remainder, over, True


def print_status(scope, text, state=State.NONE, scope_color=Fore.BLUE):  # pylint: disable=R0914
    """Print a line with a scope text, a normal text and right aligned a state

    :param scope: Text for the scope (will be blue an in square brackets
    :param text: Normal text
    :param state: State type of the message
    :param scope_color: color for scope text (default: blue)
    :return:
    """
    scope_len = len(scope) + 3  # 2 x brackets, 1 x space
    if state != State.NONE:
        state_len = max(len(entry.name) for entry in State) + 5
    else:
        state_len = 0
    terminal_width, _ = shutil.get_terminal_size((80, 24))
    text_len = terminal_width - scope_len - state_len

    scope_txt = scope_color + '[' + scope + '] ' + Style.RESET_ALL
    state_txt = ''
    for line, _, last in split_text(text, text_len):
        cor_text_len = correction_text_length(text) + text_len
        text_format = '{:<%d}{:<%d}{:>%d}' % (scope_len, cor_text_len, state_len)
        if last and state != State.NONE:
            if state == State.OK:
                color = Back.GREEN + Fore.BLACK
            elif state == State.FAIL:
                color = Back.RED + Fore.BLACK
            else:  # pragma: no cover
                color = Back.YELLOW + Fore.BLACK  # pragma no cover
            state_txt = color + '[ ' + state.name + ' ]' + Style.RESET_ALL
        print(text_format.format(scope_txt, line, state_txt))
        scope_txt = ''


def correction_text_length(text):
    """correct the text length for text with escape sequences
    :param text: text with escape characters
    :return: difference between the text and the text without escape chars
    """
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    unescaped_text = ansi_escape.sub('', text)
    return len(text) - len(unescaped_text)


def print_err(text):
    """Print a red [Error] in front of the given text

    :param text: The text to print
    :returns:
    """
    print_status(scope='ERROR', text=text, state=State.NONE, scope_color=Fore.RED)
