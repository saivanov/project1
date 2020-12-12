from pathlib import Path
from subprocess import run
from settings import DATA_SET_PATH
from csv import reader


data_set_path = Path(DATA_SET_PATH)

with open(data_set_path/'public_lecture_1.csv', 'rt') as manifest:
    manifest_reader = reader(manifest)
    for row in manifest_reader:
        run(['oggdec', data_set_path/row[0]])
