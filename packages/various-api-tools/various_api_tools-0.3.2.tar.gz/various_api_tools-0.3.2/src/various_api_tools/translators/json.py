"""Module for translating JSON decoding errors into user-friendly Russian messages.

This module provides a utility class that converts Python's `JSONDecodeError`
exceptions into more descriptive and readable error messages in Russian.
It is useful for improving the end-user experience when parsing JSON data.

"""

from json import JSONDecodeError
from typing import Final

BASE_JSON_ERROR_MESSAGE: Final[str] = "Ошибка конвертации в формате JSON.\n"


class JSONDecodeErrorTranslator:
    """Translates JSONDecodeError messages into user-friendly Russian descriptions.

    This class provides a method to convert Python's JSONDecodeError exceptions
    into more readable error messages for end users.

    """

    @classmethod
    def translate(
        cls,
        error: JSONDecodeError,
        *,
        msg: str = BASE_JSON_ERROR_MESSAGE,
        line_number: int | None = None,
    ) -> str:
        """Translate a JSONDecodeError into a human-readable message in Russian.

        Args:
            error: The JSONDecodeError instance to translate.
            msg: Optional base message to prepend. Defaults to BASE_JSON_ERROR_MESSAGE.
            line_number: Optional line number for better context.

        Returns:
            A string containing the translated error message(position and description).

        Raises:
            TypeError: If 'error' is not an instance of JSONDecodeError.

        Example:
            ```python
            try:
                json.loads('{"name": "Alice",}')
            except JSONDecodeError as e:
                print(DecodeErrorTranslator.translate(e))

            #> Ошибка конвертации в формате JSON.
            #> Позиция: 16.
            #> Описание: не правильно используются двойные кавычки.
            ```

        """
        if line_number is not None:
            msg += f"Строка: {line_number}, позиция {error.pos}.\n"
        else:
            msg += f"Позиция: {error.pos}.\n"
        exc_msg = error.msg

        if "Expecting" in exc_msg and "delimiter" in exc_msg:
            msg += "Описание: ожидается разделитель."
        elif "Expecting property name enclosed in double quotes" in exc_msg:
            msg += "Описание: не правильно используются двойные кавычки."
        elif "Expecting value" in exc_msg:
            msg += "Описание: ожидается значение."
        elif "Extra data" in exc_msg:
            msg += "Описание: обнаружены дополнительные данные."
        elif "Invalid" in exc_msg and "escape" in exc_msg:
            msg += "Описание: обнаружены недопустимые экранирующие символы."
        elif "Invalid control character at" in exc_msg:
            msg += "Описание: обнаружен неэкранированный контрольный символ."
        elif "Unterminated string starting at" in exc_msg:
            msg += "Описание: не правильно заверена закрывающая кавычка."
        else:
            msg += "Описание: неизвестная ошибка."

        return msg
