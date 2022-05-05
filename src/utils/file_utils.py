import os

from werkzeug.datastructures import FileStorage

ROOT = os.path.join(os.path.pardir, 'local_database')


def save_file(file: FileStorage, dir_path, file_name):
    file.seek(0)
    path = os.path.join(ROOT, dir_path, file_name)
    file.save(path)
