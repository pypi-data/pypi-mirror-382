# emoji-index

This is a lightweight extension to the excellent [https://github.com/carpedm20/emoji/]emoji library that provides a simple index / traversal of emoji characters to assist with selection menus.

## Using the Project

```python
from emoji_index import emoji_index

emoji_index.set_version("13.0")

print(emoji_index.version)

for group in emoji_index.groups:
    print(group)
    for subgroup in emoji_index[group].subgroups:
        print(subgroup)
        for emoji in emoji_index[group][subgroup]:
            print(emoji)
```

## Known Limitations

Multi-person grouping emojis are not supported, as these require special handling that is at the moment out of scope. (https://www.unicode.org/reports/tr51/#MultiPersonGroupingsTable)

Additionally, hair component modifiers are not presently supported. (https://www.unicode.org/reports/tr51/#hair_components)

## Licensing

This project is released under the Apache 2.0 License. See the license file for the Apache 2.0 License.

Note that the project also contains data by the Unicode Consortium, which is licensed under the Unicode License Agreement. See the license file for the Unicode License Agreement Reference.