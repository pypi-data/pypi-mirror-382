import json
import sys

import pytest

from src.various_api_tools.translators.json import JSONDecodeErrorTranslator


class TestDecodeErrorTranslator:
    @pytest.mark.skipif(sys.version_info >= (3, 13), reason="not for Python 3.13")
    @pytest.mark.parametrize(
        "input_data, expected_output, error_msg",
        [
            # Ошибка: ожидается разделитель (Expecting delimiter)
            (
                "[1, 2 3]",
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 6.\n"
                "Описание: ожидается разделитель.",
            ),
            (
                '{"name": "Alice",}',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 17.\n"
                "Описание: не правильно используются двойные кавычки.",
            ),
            (
                '[{"id": 1}',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 10.\n"
                "Описание: ожидается разделитель.",
            ),
            # Ошибка: не правильно используются двойные кавычки
            (
                '{"name": "Alice"',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 16.\n"
                "Описание: ожидается разделитель.",
            ),
            # Ошибка: ожидается значение
            (
                "",
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 0.\n"
                "Описание: ожидается значение.",
            ),
            (
                '{"id": }',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 7.\n"
                "Описание: ожидается значение.",
            ),
            # Ошибка: обнаружены дополнительные данные
            (
                '\n{"name": "Alice"}\n\n{"name": "Bob"}\n',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 20.\n"
                "Описание: обнаружены дополнительные данные.",
            ),
            # Ошибка: недопустимые экранирующие символы
            (
                '{"text": "Hello\x00World"}',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 15.\n"
                "Описание: обнаружен неэкранированный контрольный символ.",
            ),
            # Ошибка: незакрытая строка
            (
                '{"name": "Alice"',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 16.\n"
                "Описание: ожидается разделитель.",
            ),
            # Корректный JSON
            (
                '[{"name": "Alice"}, {"name": "Bob"}]',
                [{"name": "Alice"}, {"name": "Bob"}],
                None,
            ),
            # Корректный JSON
            (
                '{"name": "Alice"}',
                {"name": "Alice"},
                None,
            ),
        ],
    )
    def test_translate_without_line_number(
        self,
        input_data,
        expected_output,
        error_msg,
    ):
        try:
            res = json.loads(input_data)
        except json.JSONDecodeError as exc:
            msg = JSONDecodeErrorTranslator.translate(error=exc)
            assert msg == error_msg
        else:
            assert res == expected_output

    @pytest.mark.skipif(sys.version_info >= (3, 13), reason="not for Python 3.13")
    @pytest.mark.parametrize(
        "input_data, expected_output, error_msg",
        [
            # Ошибка: ожидается разделитель (Expecting delimiter)
            (
                "[1, 2 3]",
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 6.\n"
                "Описание: ожидается разделитель.",
            ),
            (
                '{"name": "Alice",}',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 17.\n"
                "Описание: не правильно используются двойные кавычки.",
            ),
            (
                '[{"id": 1}',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 10.\n"
                "Описание: ожидается разделитель.",
            ),
            # Ошибка: не правильно используются двойные кавычки
            (
                '{"name": "Alice"',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 16.\n"
                "Описание: ожидается разделитель.",
            ),
            # Ошибка: ожидается значение
            (
                "",
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 0.\n"
                "Описание: ожидается значение.",
            ),
            (
                '{"id": }',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 7.\n"
                "Описание: ожидается значение.",
            ),
            # Ошибка: обнаружены дополнительные данные
            (
                '\n{"name": "Alice"}\n\n{"name": "Bob"}\n',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 20.\n"
                "Описание: обнаружены дополнительные данные.",
            ),
            # Ошибка: недопустимые экранирующие символы
            (
                '{"text": "Hello\x00World"}',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 15.\n"
                "Описание: обнаружен неэкранированный контрольный символ.",
            ),
            # Ошибка: незакрытая строка
            (
                '{"name": "Alice"',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 16.\n"
                "Описание: ожидается разделитель.",
            ),
            # Корректный JSON
            (
                '[{"name": "Alice"}, {"name": "Bob"}]',
                [{"name": "Alice"}, {"name": "Bob"}],
                None,
            ),
            # Корректный JSON
            (
                '{"name": "Alice"}',
                {"name": "Alice"},
                None,
            ),
        ],
    )
    def test_translate_with_line_number(self, input_data, expected_output, error_msg):
        try:
            res = json.loads(input_data)
        except json.JSONDecodeError as exc:
            msg = JSONDecodeErrorTranslator.translate(error=exc, line_number=6)
            assert msg == error_msg
        else:
            assert res == expected_output


class TestDecodeErrorTranslatorForPython313:
    @pytest.mark.skipif(sys.version_info < (3, 13), reason="for Python 3.13")
    @pytest.mark.parametrize(
        "input_data, expected_output, error_msg",
        [
            # Ошибка: ожидается разделитель (Expecting delimiter)
            (
                "[1, 2 3]",
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 6.\n"
                "Описание: ожидается разделитель.",
            ),
            (
                '{"name": "Alice",}',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 16.\n"
                "Описание: неизвестная ошибка.",
            ),
            (
                '[{"id": 1}',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 10.\n"
                "Описание: ожидается разделитель.",
            ),
            # Ошибка: не правильно используются двойные кавычки
            (
                '{"name": "Alice"',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 16.\n"
                "Описание: ожидается разделитель.",
            ),
            # Ошибка: ожидается значение
            (
                "",
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 0.\n"
                "Описание: ожидается значение.",
            ),
            (
                '{"id": }',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 7.\n"
                "Описание: ожидается значение.",
            ),
            # Ошибка: обнаружены дополнительные данные
            (
                '\n{"name": "Alice"}\n\n{"name": "Bob"}\n',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 20.\n"
                "Описание: обнаружены дополнительные данные.",
            ),
            # Ошибка: недопустимые экранирующие символы
            (
                '{"text": "Hello\x00World"}',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 15.\n"
                "Описание: обнаружен неэкранированный контрольный символ.",
            ),
            # Ошибка: незакрытая строка
            (
                '{"name": "Alice"',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Позиция: 16.\n"
                "Описание: ожидается разделитель.",
            ),
            # Корректный JSON
            (
                '[{"name": "Alice"}, {"name": "Bob"}]',
                [{"name": "Alice"}, {"name": "Bob"}],
                None,
            ),
            # Корректный JSON
            (
                '{"name": "Alice"}',
                {"name": "Alice"},
                None,
            ),
        ],
    )
    def test_translate_without_line_number(
        self,
        input_data,
        expected_output,
        error_msg,
    ):
        try:
            res = json.loads(input_data)
        except json.JSONDecodeError as exc:
            msg = JSONDecodeErrorTranslator.translate(error=exc)
            assert msg == error_msg
        else:
            assert res == expected_output

    @pytest.mark.skipif(sys.version_info < (3, 13), reason="for Python 3.13")
    @pytest.mark.parametrize(
        "input_data, expected_output, error_msg",
        [
            # Ошибка: ожидается разделитель (Expecting delimiter)
            (
                "[1, 2 3]",
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 6.\n"
                "Описание: ожидается разделитель.",
            ),
            (
                '{"name": "Alice",}',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 16.\n"
                "Описание: неизвестная ошибка.",
            ),
            (
                '[{"id": 1}',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 10.\n"
                "Описание: ожидается разделитель.",
            ),
            # Ошибка: не правильно используются двойные кавычки
            (
                '{"name": "Alice"',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 16.\n"
                "Описание: ожидается разделитель.",
            ),
            # Ошибка: ожидается значение
            (
                "",
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 0.\n"
                "Описание: ожидается значение.",
            ),
            (
                '{"id": }',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 7.\n"
                "Описание: ожидается значение.",
            ),
            # Ошибка: обнаружены дополнительные данные
            (
                '\n{"name": "Alice"}\n\n{"name": "Bob"}\n',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 20.\n"
                "Описание: обнаружены дополнительные данные.",
            ),
            # Ошибка: недопустимые экранирующие символы
            (
                '{"text": "Hello\x00World"}',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 15.\n"
                "Описание: обнаружен неэкранированный контрольный символ.",
            ),
            # Ошибка: незакрытая строка
            (
                '{"name": "Alice"',
                None,
                "Ошибка конвертации в формате JSON.\n"
                "Строка: 6, позиция 16.\n"
                "Описание: ожидается разделитель.",
            ),
            # Корректный JSON
            (
                '[{"name": "Alice"}, {"name": "Bob"}]',
                [{"name": "Alice"}, {"name": "Bob"}],
                None,
            ),
            # Корректный JSON
            (
                '{"name": "Alice"}',
                {"name": "Alice"},
                None,
            ),
        ],
    )
    def test_translate_with_line_number(self, input_data, expected_output, error_msg):
        try:
            res = json.loads(input_data)
        except json.JSONDecodeError as exc:
            msg = JSONDecodeErrorTranslator.translate(error=exc, line_number=6)
            assert msg == error_msg
        else:
            assert res == expected_output
