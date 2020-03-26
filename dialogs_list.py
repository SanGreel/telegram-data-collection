import json
import os

if __name__ == "__main__":
    meta_folder = 'data/meta/'
    files = os.listdir(meta_folder)
    for f in files:
        path = meta_folder + f
        print(path)

        #TODO: fix error with encoding
        with open(f, 'r', encoding="ISO-8859-1") as read_file:
            dialogs_list = json.load(read_file)
            for i in dialogs_list['id']['name']:
                print(i)











