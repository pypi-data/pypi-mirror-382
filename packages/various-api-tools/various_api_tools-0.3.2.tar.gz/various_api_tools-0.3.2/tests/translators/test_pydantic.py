from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import UUID5, BaseModel, ValidationError

from src.various_api_tools.translators.pydantic import PydanticValidationErrorTranslator


class TestValidationErrorTranslator:
    def test_bool_errors(self):
        class Model(BaseModel):
            a: bool
            b: bool
            c: bool

        try:
            Model(a="test", b=None)
        except ValidationError as exc:
            message = PydanticValidationErrorTranslator.translate(exc.errors())
            assert isinstance(message, str)
            assert (
                'Поле: "a" заполнено неверно: "\'test\'". Ошибка: "Невалидное значение для логического типа(bool)";'
                in message
            )
            assert (
                'Поле: "b" заполнено неверно: "None". Ошибка: "Невалидное значение для логического типа(bool)";'
                in message
            )
            assert 'Поле: "c". Ошибка: "Не заполнено обязательное поле";' in message
        else:
            raise AssertionError("Тест должен был обработать ValidationError")

    def test_int_errors(self):
        class Model(BaseModel):
            a: int
            b: int
            c: int
            d: int
            e: int

        try:
            Model(a=0.5, b="test", c="1" * 4_301, d=None)
        except ValidationError as exc:
            message = PydanticValidationErrorTranslator.translate(exc.errors())
            assert isinstance(message, str)
            assert (
                'Поле: "a" заполнено неверно: "0.5". Ошибка: "Невалидное значение для целочисленного числа(int)";'
                in message
            )
            assert (
                'Поле: "b" заполнено неверно: "\'test\'". Ошибка: "Невалидное значение для целочисленного числа(int)";'
                in message
            )
            assert (
                f'Поле: "c" заполнено неверно: "\'{"1" * 4_301}\'". Ошибка: "Невалидное значение для целочисленного числа(int)";'
                in message
            )
            assert (
                'Поле: "d" заполнено неверно: "None". Ошибка: "Невалидное значение для целочисленного числа(int)";'
                in message
            )
            assert 'Поле: "e". Ошибка: "Не заполнено обязательное поле";' in message
        else:
            raise AssertionError("Тест должен был обработать ValidationError")

    def test_dict_errors(self):
        class Model(BaseModel):
            a: dict
            b: dict

        try:
            Model(a=["1", "2"])
        except ValidationError as exc:
            message = PydanticValidationErrorTranslator.translate(exc.errors())
            assert isinstance(message, str)
            assert (
                'Поле: "a" заполнено неверно: "[\'1\', \'2\']". Ошибка: "Невалидное значение словаря";'
                in message
            )
            assert 'Поле: "b". Ошибка: "Не заполнено обязательное поле";' in message
        else:
            raise AssertionError("Тест должен был обработать ValidationError")

    def test_enum_errors(self):
        class MyEnum(str, Enum):
            option = "option"

        class Model(BaseModel):
            a: MyEnum
            b: MyEnum

        try:
            Model(a="other_option")
        except ValidationError as exc:
            message = PydanticValidationErrorTranslator.translate(exc.errors())
            assert isinstance(message, str)
            assert (
                'Поле: "a" заполнено неверно: "\'other_option\'". Ошибка: "Невалидное значение Enum";'
                in message
            )
            assert 'Поле: "b". Ошибка: "Не заполнено обязательное поле";' in message

    def test_float_errors(self):
        class Model(BaseModel):
            a: float
            b: float
            c: float

        try:
            Model(a="test", b=None)
        except ValidationError as exc:
            message = PydanticValidationErrorTranslator.translate(exc.errors())
            assert isinstance(message, str)
            assert (
                'Поле: "a" заполнено неверно: "\'test\'". Ошибка: "Невалидное значение числа с плавающей точкой(float)";'
                in message
            )
            assert (
                'Поле: "b" заполнено неверно: "None". Ошибка: "Невалидное значение числа с плавающей точкой(float)";'
                in message
            )
            assert 'Поле: "c". Ошибка: "Не заполнено обязательное поле"' in message

    def test_uuid_errors(self):
        class Model(BaseModel):
            a: UUID
            b: UUID
            c: UUID5
            d: UUID

        try:
            Model(
                a="12345678-124-1234-1234-567812345678",
                b=1234567812412341234567812345678,
                c="a6cc5730-2261-11ee-9c43-2eb5a363657c",
            )
        except ValidationError as exc:
            message = PydanticValidationErrorTranslator.translate(exc.errors())
            assert isinstance(message, str)
            assert (
                'Поле: "a" заполнено неверно: "\'12345678-124-1234-1234-567812345678\'". Ошибка: "Невалидное значение для UUID";'
                in message
            )
            assert (
                'Поле: "b" заполнено неверно: "1234567812412341234567812345678". Ошибка: "Невалидное значение для UUID";'
                in message
            )
            assert (
                'Поле: "c" заполнено неверно: "\'a6cc5730-2261-11ee-9c43-2eb5a363657c\'". Ошибка: "Невалидное значение для UUID";'
                in message
            )
            assert 'Поле: "d". Ошибка: "Не заполнено обязательное поле";' in message

    def test_str_errors(self):
        class Model(BaseModel):
            a: str
            b: str

        try:
            Model(a=1)
        except ValidationError as exc:
            message = PydanticValidationErrorTranslator.translate(exc.errors())
            assert isinstance(message, str)
            assert (
                'Поле: "a" заполнено неверно: "1". Ошибка: "Невалидное строковое значение(str)";'
                in message
            )
            assert 'Поле: "b". Ошибка: "Не заполнено обязательное поле";' in message

    def test_list_errors(self):
        class Model(BaseModel):
            a: list[int]
            b: list[int]

        try:
            Model(a=1)
        except ValidationError as exc:
            message = PydanticValidationErrorTranslator.translate(exc.errors())
            assert isinstance(message, str)
            assert (
                'Поле: "a" заполнено неверно: "1". Ошибка: "Невалидное значение списка";'
                in message
            )
            assert 'Поле: "b". Ошибка: "Не заполнено обязательное поле";' in message

    def test_date_errors(self):
        class Model(BaseModel):
            a: date
            b: date

        try:
            Model(a=None)
        except ValidationError as exc:
            message = PydanticValidationErrorTranslator.translate(exc.errors())
            assert isinstance(message, str)
            assert (
                'Поле: "a" заполнено неверно: "None". Ошибка: "Невалидное значение даты(date)";'
                in message
            )
            assert 'Поле: "b". Ошибка: "Не заполнено обязательное поле";' in message

    def test_datetime_errors(self):
        class Model(BaseModel):
            a: datetime
            b: datetime
            c: datetime

        try:
            # there is no 13th month
            Model(a="2023-13-01", b=None)
        except ValidationError as exc:
            message = PydanticValidationErrorTranslator.translate(exc.errors())
            assert isinstance(message, str)
            assert (
                'Поле: "a" заполнено неверно: "\'2023-13-01\'". Ошибка: "Невалидное значение даты и времени(datetime)";'
                in message
            )
            assert (
                'Поле: "b" заполнено неверно: "None". Ошибка: "Невалидное значение даты и времени(datetime)";'
                in message
            )
            assert 'Поле: "c". Ошибка: "Не заполнено обязательное поле";' in message
