from settings import *
from typing import List

def import_image(*path, format = '.png', alpha = True) -> pg.Surface:
    full_path = join(*path) + format 
    if alpha:
        return pg.image.load(full_path).convert_alpha()
    else:
        return pg.image.load(full_path).convert()

def import_folder(*path) -> List[pg.Surface]:
    frames = []
    for folder_path, _, file_names in walk(join(*path)):
        for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
              full_path = join(folder_path, file_name)
              frames.append(pg.image.load(full_path).convert_alpha())
    return frames

def audio_importer(*path):
    audio_dict = {}
    for folder_path, _, file_names in walk(join(*path)):
        for file_name in file_names:
            full_path = join(folder_path, file_name)
            audio_dict[file_name.split('.')[0]] = pg.mixer.Sound(full_path)
    return audio_dict