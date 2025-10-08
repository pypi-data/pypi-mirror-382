import re

from decimal import Decimal

import emoji as emojilib

from .emoji_data import emoji_text
from ..objects.emoji import _EmojiInt, _EmojiQual


class EmojiData:
    _UNSUPPORTED_NAME = ['handshake', 'people with bunny ears', 'men with bunny ears', 'women with bunny ears',
                         'people wrestling', 'men wrestling', 'women wrestling',
                         'woman and man holding hands', 'men holding hands', 'women holding hands',
                         'people holding hands', 'kiss', 'couple with heart', 'family']

    _UNSUPPORTED_MODIFIER = ['beard', 'bald', 'blond hair', 'white hair', 'curly hair', 'red hair']

    def __init__(self):
        data = {}
        group = None
        subgroup = None
        for line in emoji_text.split('\n'):
            line = line.strip()
            if line == '':
                continue
            elif line.startswith('#'):
                if line.startswith('# group:'):
                    group = line[9:].strip()
                    data[group] = {}
                elif line.startswith('# subgroup:'):
                    subgroup = line[12:].strip()
                    data[group][subgroup] = []
            else:
                emoji = EmojiData._parse_emoji_row(row=line)
                if emoji is not None and emoji.qual is _EmojiQual.FullyQualified:
                    data[group][subgroup].append(emoji)
        self.data = data

    def _parse_emoji_row(row: str) -> _EmojiInt:
        characters = row[:55].strip().split(' ')
        emoji = ''.join([chr(int(c, 16)) for c in characters])
        qualification = _EmojiQual(row[56:76].strip())
        version = Decimal(re.search(r'E\d+\.\d+', row[76:].strip()).group(0)[1:])
        raw_name = re.search(r'E\d+\.\d+(.*)', row[76:].strip()).group(1).strip()
        split_name = raw_name.split(': ')

        if len(split_name) > 1:
            if split_name[0] in ['flag', 'keycap']:
                name = ": ".join(split_name)
                child_of = None
            else:
                split_name = [split_name[0]] + [s.strip() for s in split_name[1].split(',')]
                if split_name[0] in EmojiData._UNSUPPORTED_NAME:
                    return None
                else:
                    for modifier in split_name[1:]:
                        if modifier in EmojiData._UNSUPPORTED_MODIFIER:
                            return None

                    name = ": ".join(split_name)
                    child_of = split_name[0]
        else:
            name = split_name[0]
            child_of = None

        return _EmojiInt(emoji=emoji, qual=qualification, version=version, name=name, child_of=child_of,
                         demojized=emojilib.demojize(emoji))
