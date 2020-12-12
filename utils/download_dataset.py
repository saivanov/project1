import os
import pathlib
import tensorflow
from urllib.parse import urlparse
from settings import DATA_SET_URL, DATA_SET_PATH


def download_data_set(data_set_url, data_set_path):
    file_name = os.path.basename(urlparse(data_set_url).path)
    data_dir = pathlib.Path(os.path.join(data_set_path, file_name.split('.')[0]))
    if not data_dir.exists():
        tensorflow.keras.utils.get_file(
            file_name,
            origin=data_set_url,
            extract=True,
            cache_dir='.', cache_subdir=data_set_path)


if __name__ == '__main__':
    download_data_set(DATA_SET_URL, DATA_SET_PATH)
