# Various_api_tools

**A lightweight utility package for common API-related tasks in Python, including JSON and Pydantic error translators that provide user-friendly Russian messages.**

### Basic Usage

```python
import json
from various_api_tools.translators.json import DecodeErrorTranslator

try:
    json.loads('{"name": "Alice",}')
except json.JSONDecodeError as e:
    print(DecodeErrorTranslator.translate(e))

# Output:
# Ошибка конвертации в формате JSON.
# Позиция: 16.
# Описание: не правильно используются двойные кавычки.
```

```python
from pydantic import BaseModel, ValidationError
from various_api_tools.translators.pydantic import ValidationErrorTranslator

class User(BaseModel):
    email: str

try:
    User(email=123)
except ValidationError as e:
    print(ValidationErrorTranslator.translate(e.errors()))

# Output:
# Поле: "email". Ошибка: "Невалидное строковое значение(str)";
```


### Installation
```bash
pip install various_api_tools
```

### License

MIT License — feel free to use it in any project! 🎉

### Documentation

[https://various-api-tools.dkurchigin.ru/](https://various-api-tools.dkurchigin.ru/)

### Author

Made with ❤️ by [@dkurchigin](https://gitverse.ru/dkurchigin)

### Gitverse

[https://gitverse.ru/dkurchigin/various-api-tools](https://gitverse.ru/dkurchigin/various-api-tools)
