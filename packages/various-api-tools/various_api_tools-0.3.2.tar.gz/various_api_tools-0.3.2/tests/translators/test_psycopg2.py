from src.various_api_tools.translators.psycopg2 import (
    BASE_PSYCOPG2_ERROR_MESSAGE,
    ErrorData,
    Psycopg2ErrorTranslator,
)


class TestPsycopg2ErrorTranslator:
    def test_get_unique_violation_error(self):
        error_msg = (
            "DETAIL:  Key (uuid)=(a6cc5730-2261-11ee-9c43-2eb5a363657c) already exists."
        )
        result = Psycopg2ErrorTranslator.get_unique_violation_error(error_msg)
        assert isinstance(result, ErrorData)
        assert result.key == "uuid"
        assert result.value == "a6cc5730-2261-11ee-9c43-2eb5a363657c"

        # No match case
        error_msg = "No violation here."
        result = Psycopg2ErrorTranslator.get_unique_violation_error(error_msg)
        assert result is None

    def test_get_check_violation_error(self):
        translator = Psycopg2ErrorTranslator(
            constraint_map={"valid_email": "Невалидный email"},
        )

        error_msg = 'violates check constraint "valid_email"'
        result = translator.get_check_violation_error(error_msg)
        assert isinstance(result, ErrorData)
        assert result.key == "valid_email"
        assert result.value == "Невалидный email"

        # Unknown constraint
        error_msg = 'violates check constraint "unknown_check"'
        result = translator.get_check_violation_error(error_msg)
        assert isinstance(result, ErrorData)
        assert result.key == "unknown_check"
        assert result.value == "Невалидная запись в БД"

        # No match case
        error_msg = "No violation here."
        result = translator.get_check_violation_error(error_msg)
        assert result is None

    def test_translate_with_unique_violation(self):
        class MockError(Exception):
            def __init__(self):
                self.pgcode = "23505"
                self.pgerror = (
                    "DETAIL:  Key (email)=(invalid@example.com) already exists."
                )

        translator = Psycopg2ErrorTranslator()
        result = translator.translate(MockError())
        assert (
            "БД уже содержит значение: ключ email, значение invalid@example.com."
            in result
        )

    def test_translate_with_check_violation(self):
        class MockError(Exception):
            def __init__(self):
                self.pgcode = "23514"
                self.pgerror = 'violates check constraint "valid_email"'

        translator = Psycopg2ErrorTranslator(
            constraint_map={"valid_email": "Невалидный email"},
        )
        result = translator.translate(MockError())
        assert (
            "Нарушено ограничение данных: ключ valid_email, значение Невалидный email."
            in result
        )

    def test_translate_with_unknown_code(self):
        class MockError(Exception):
            def __init__(self):
                self.pgcode = "00000"
                self.pgerror = ""

        translator = Psycopg2ErrorTranslator()
        result = translator.translate(MockError())
        assert result == BASE_PSYCOPG2_ERROR_MESSAGE

    def test_translate_with_custom_messages(self):
        class MockError(Exception):
            def __init__(self):
                self.pgcode = "23503"
                self.pgerror = ""

        custom_code_map = {
            23503: "Указан несуществующий внешний идентификатор",
        }
        translator = Psycopg2ErrorTranslator(code_map=custom_code_map)
        result = translator.translate(MockError())
        assert result == "Указан несуществующий внешний идентификатор."
