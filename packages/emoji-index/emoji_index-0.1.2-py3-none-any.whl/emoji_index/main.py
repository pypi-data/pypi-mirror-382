from decimal import Decimal

from .data.emojis import EmojiData
from .objects.emoji import Emoji, _EmojiVersion


class EmojiGroup:

    def __init__(self, data_block: dict):
        self.__parsed_data = data_block

    # Return a list of subgroups within the group
    @property
    def subgroups(self) -> list[str]:
        return list(self.__parsed_data.keys())

    # Return the specified subgroup
    def __getitem__(self, subgroup: str) -> list[Emoji]:
        return self.__parsed_data[subgroup]


class EmojiIndex:

    def __init__(self):
        self.__version = _EmojiVersion.E15_1
        self.__data = EmojiData()
        self.__load()

    # Build a modified version of EmojiData for the specified version
    def __load(self):
        self.__parsed_data = {}
        for group, data in self.__data.data.items():
            temp_group_data = {}
            for subgroup, data2 in data.items():
                temp_data = {}
                for emoji in data2:
                    if emoji.version <= Decimal(self.__version.value):
                        if emoji.child_of is None:
                            temp_data[emoji.name] = (
                                Emoji(emoji=emoji.emoji, name=emoji.name, alias=emoji.demojized))
                        else:
                            if temp_data[emoji.child_of].variants is None:
                                temp_data[emoji.child_of].variants = [emoji.emoji]
                            else:
                                temp_data[emoji.child_of].variants.append(emoji.emoji)
                if len(temp_data) > 0:
                    temp_group_data[subgroup] = list(temp_data.values())
            if len(temp_group_data) > 0:
                self.__parsed_data[group] = temp_group_data

    @property
    def version(self) -> _EmojiVersion:
        return self.__version

    def set_version(self, version: str):
        if version in _EmojiVersion.__members__.values():
            self.__version = _EmojiVersion(version)
            self.__load()
        else:
            raise ValueError(f"Version {version} not supported")

    # Return a list of groups
    @property
    def groups(self) -> list[str]:
        return list(self.__parsed_data.keys())

    # Return the specified group
    def __getitem__(self, group: str) -> EmojiGroup:
        return EmojiGroup(data_block=self.__parsed_data[group])
