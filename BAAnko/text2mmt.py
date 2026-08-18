import json
from os.path import expanduser
from pprint import pp
from shutil import copy
from tkinter.filedialog import askopenfilename

chat_tiles = json.load(
    open(expanduser(r"~\Momotalk\ChatTiles\ChatTilesGroups.json"), encoding="utf-8")
)
for i, group in enumerate(chat_tiles):
    pp(f"{i} {group["groupName"]}")
group_index = int(input(f"Which one?(0~{len(chat_tiles) - 1})"))

for i, tile in enumerate(tiles := chat_tiles[group_index]["chatTiles"]):
    pp(f"{i} {tile["tileTitle"]}{tile["tileSubtitle"]}")
tile_index = int(input(f"Which one?(0~{len(tiles)-1})"))

work_tile = json.load(
    open(
        filename := expanduser(
            rf"~\Momotalk\Messages\{tiles[tile_index]["chatTileUID"]}.json"
        ),
        encoding="utf-8",
    )
)
copy(filename, filename + ".bak")

text_filename = askopenfilename(
    defaultextension=".txt", filetypes=(("文本文档", ".txt"),)
)

if text_filename is None:
    exit()

text_file = open(text_filename, encoding="utf-8")

while line := text_file.readline():
    work_tile.append(
        {
            "senderId": 3,
            "senderSkinIndex": 0,
            "messageType": 0,
            "sendMessageName": "",
            "messageContentList": [line.strip('\n').strip()],
            "boxAlign": False,
            "storageInfo": {},
        }
    )

json.dump(work_tile, open(filename, "w", encoding="utf-8"))
