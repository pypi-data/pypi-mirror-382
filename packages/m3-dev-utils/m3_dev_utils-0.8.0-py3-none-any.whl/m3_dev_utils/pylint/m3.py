# coding: utf-8
from pylint.checkers import BaseChecker
from pylint.interfaces import IRawChecker
from six import b


class M3Checker(BaseChecker):

    """Проверки кода на соответствие стандартам для платформы M3.

    Перечень проверок:

      * Проверка объявления кодировки python-модулей (должна быть указана
        всегда в следующем виде: ``# coding: utf-8``).
    """

    __implements__ = IRawChecker

    name = 'm3'
    priority = -1

    msgs = {
        'W2000': (
            'Объявление кодировки файла не соответствует стандарту: %s',
            'encoding-declaration',
            'Допустимый способ объявления кодировки: # coding: utf-8.'
        ),
        'W2001': (
            'Пустая строка перед импортами',
            'empty-line-before-import',
            'Удалить все пустые строки перед импортами',
        ),
    }

    def process_module(self, module):
        encoding_declaration_checked = False
        empty_line_checked = False

        lines = []
        with module.stream() as stream:
            for line_number, line_content in enumerate(stream):
                lines.append(line_content)
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Проверка объявления кодировки файла.
                if not encoding_declaration_checked:
                    if line_content.startswith(b('#!')):
                        continue
                    if line_content != b('# coding: utf-8\n'):
                        self.add_message(
                            'encoding-declaration',
                            line=line_number,
                            args=(line_content,)
                        )
                    encoding_declaration_checked = True
                    continue
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                if line_content.lstrip().startswith(b('#')):
                    continue
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Проверка на отсутствие пустых строк перед импортами.
                if not empty_line_checked and line_content.strip():
                    empty_line_checked = True
                    if (
                        (
                            line_content.startswith(b('from ')) or
                            line_content.startswith(b('import '))
                        ) and
                        any(not l.strip() for l in lines[:-1])
                    ):
                        self.add_message(
                            'empty-line-before-import',
                            line=line_number,
                        )
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
