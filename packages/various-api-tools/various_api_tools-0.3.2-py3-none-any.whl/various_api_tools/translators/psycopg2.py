"""Module for translating PostgreSQL (psycopg2) database errors into messages.

This module provides a utility class to parse and translate psycopg2 error messages
into readable Russian strings suitable for end-user feedback.
"""

import re
from dataclasses import dataclass
from typing import Any, Final

from psycopg2._psycopg import Error

BASE_PSYCOPG2_ERROR_MESSAGE: Final[str] = (
    "Ошибка во время сохранения/изменения в базе данных. Проверьте исходные данные."
)
UNIQUE_VIOLATION_PATTERN: Final[str] = r"DETAIL:.*(Key|Ключ).*\((.*?)\)=\((.*?)\)"
CHECK_VIOLATION_PATTERN: Final[str] = r'violates check constraint.*?"(.*?)"'

UNKNOWN_CHECK_DESCRIPTION: Final[str] = "Невалидная запись в БД"
DEFAULT_CODE_DESCRIPTION_MAP: Final[dict[int, str]] = {
    23503: "Указан несуществующий идентификатор связанного объекта",
    23505: "БД уже содержит значение",
    23514: "Нарушено ограничение данных",
}


@dataclass
class ErrorData:
    """Holds extracted key-value pairs from database error messages."""

    key: str
    value: Any


class Psycopg2ErrorTranslator:
    """Translates psycopg2 database errors into human-readable Russian messages.

    This class extracts error details from PostgreSQL exceptions and converts them
    into clear, user-friendly messages based on error codes and patterns.

    """

    code_map: dict[int, str]
    constraint_map: dict[str, str]

    def __init__(
        self,
        *,
        code_map: dict[int, str] | None = None,
        constraint_map: dict[str, str] | None = None,
    ) -> None:
        """Initialize the translator with optional custom error message mappings.

        Args:
            code_map: Optional mapping of PostgreSQL error codes to messages.
            constraint_map: Optional mapping of check constraints to descriptions.

        """
        if constraint_map is not None:
            self.constraint_map = constraint_map
        else:
            self.constraint_map = {}

        if code_map is not None:
            self.code_map = code_map
        else:
            self.code_map = DEFAULT_CODE_DESCRIPTION_MAP

    @classmethod
    def get_unique_violation_error(cls, error_msg: str) -> ErrorData:
        """Extract key and value from a unique constraint violation message.

        Args:
            error_msg: Raw error message string.

        Returns:
            An `ErrorData` object with extracted key and value, or None if no match.

        Example:
            ```python
            error_msg = "DETAIL:  Key (value)=(a6cc5730) already exists."
            result = Psycopg2ErrorTranslator.get_unique_violation_error(error_msg)
            #> ErrorData(key='uuid', value='a6cc5730-2261-11ee-9c43-2eb5a363657c')
            ```

        """
        data: ErrorData | None = None

        pattern = re.compile(UNIQUE_VIOLATION_PATTERN)
        matched = pattern.search(error_msg)

        if matched is not None:
            data = ErrorData(key=matched.group(2), value=matched.group(3))

        return data

    def get_check_violation_error(self, error_msg: str) -> ErrorData | None:
        """Extract constraint name and description from a check constraint violation.

        Args:
            error_msg: Raw error message string.

        Returns:
            An `ErrorData` object with constraint name and description, or None.

        Example:
            ```python
            error_msg = 'violates check constraint "valid_email"'
            result = translator.get_check_violation_error(error_msg)
            #> ErrorData(key='valid_email', value='Невалидный email')
            ```

        """
        data: ErrorData | None = None

        pattern = re.compile(CHECK_VIOLATION_PATTERN)
        matched = pattern.search(error_msg)
        if matched is not None:
            check_constraint = matched.group(1)
            constraint_description = self.constraint_map.get(
                check_constraint,
                UNKNOWN_CHECK_DESCRIPTION,
            )
            data = ErrorData(key=check_constraint, value=constraint_description)

        return data

    def translate(
        self,
        error: Error,
        *,
        msg: str = BASE_PSYCOPG2_ERROR_MESSAGE,
    ) -> str:
        """Translate a psycopg2 Error into a user-friendly Russian message.

        Args:
            error: A psycopg2 Error instance.
            msg: Optional base message to use if no specific translation is found.

        Returns:
            A string containing the translated error message.

        Example:
            ```python
            translator = Psycopg2ErrorTranslator()
            result = translator.translate(exc)
            #> "БД уже содержит значение: ключ email, значение invalid@example.com."
            ```

        """
        pgcode = int(value) if (value := error.pgcode) is not None else None
        if pgcode is not None:
            msg_prefix: str | None = self.code_map.get(pgcode)
            data: ErrorData | None = None

            if pgcode == 23514:  # noqa: PLR2004
                data = self.get_check_violation_error(error_msg=error.pgerror)
            elif pgcode in {23505, 23503}:
                data = self.get_unique_violation_error(error_msg=error.pgerror)

            if data:
                if msg_prefix:
                    msg = f"{msg_prefix}: ключ {data.key}, значение {data.value}."
            elif msg_prefix:
                msg = f"{msg_prefix}."

        return msg
