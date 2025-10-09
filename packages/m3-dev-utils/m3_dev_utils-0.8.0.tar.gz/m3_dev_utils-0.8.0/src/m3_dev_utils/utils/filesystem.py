# coding: utf-8
"""Модуль содержит функции работы с файлами."""
import os
import six

if six.PY2:
    from pathlib2 import Path
else:
    from pathlib import Path


CODING_HEADER = '# coding: utf-8\n'


def _is_coding_header(header):
    """Определена ли у файла кодировка.

    :param str header: первая строка проверяемого файла.
    :rtype bool
    """
    return (
        header.startswith('#') and
        not header.startswith('#!') and
        'coding' in header.lower()
    )


def fix_file_coding(file_path):
    """Исправляет объявление кодировки в файле.

    :param pathlib.Path file_path: путь до файла.
    """
    assert file_path.name.endswith('.py'), file_path

    with open(file_path, 'r') as f:
        header = f.readline()
        content = f.read()

    if _is_coding_header(header):
        if header == CODING_HEADER:
            header = None
        else:
            header = CODING_HEADER
    else:
        if header.startswith('#!'):
            header = None
        else:
            content = header + content
            header = CODING_HEADER

    if header is not None:
        with open(file_path, 'w') as f:
            f.write(header)
            f.write(content)


def get_coding_declaration(file_path):
    """Возвращает строку с объявлением кодировки в файле.

    :param pathlib.Path file_path: путь до файла.
    :return кортеж вида (задана ли кодировка, заголовок)
    :rtype tuple
    """
    assert file_path.name.endswith('.py'), file_path

    with open(file_path, 'r') as python_file:
        header = python_file.readline()

    if _is_coding_header(header):
        if header == CODING_HEADER:
            result = True, None
        else:
            result = False, header
    else:
        result = None, None

    return result


def delete_files(root, extension, log=False):
    """Удаляет файлы с указанным расширением.

    :param pathlib.Path root: корень, откуда будем удалять.
    :param str extension: расширение удаляемых файлов.
    :param bool log: логировать ли удаленные файлы.
    """
    if root.is_dir():
        for dir_path, _, file_names in os.walk(root):
            for file_name in file_names:
                if not file_name.endswith('.' + extension):
                    continue
                file_path = Path(dir_path, file_name)
                if log:
                    print('REMOVE:', file_path.relative_to(root).as_posix())
                file_path.unlink()

    elif root.is_file():
        if log:
            print('REMOVE:', file_path.relative_to(root).as_posix())
        root.unlink()
