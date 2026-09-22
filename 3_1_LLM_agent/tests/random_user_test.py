from llm_agent.tool_randomuser import RandomUserTool


def test_generates_user_with_default_fields():
    """Базовый сценарий: одна запись, все поля на месте."""
    tool = RandomUserTool()
    result = tool.use(count=1)

    # Ответ — валидный JSON-массив
    assert result.strip().startswith("[")
    assert result.strip().endswith("]")
    # Вычисляемые поля присутствуют
    assert "full_name" in result
    assert "address" in result
    # Реальные данные из randomuser.me
    assert "@" in result  # email есть


def test_include_fields_filters_output():
    """include_fields оставляет только запрошенные поля."""
    tool = RandomUserTool()
    result = tool.use(count=1, include_fields=["full_name", "email"])

    assert "full_name" in result
    assert "email" in result
    # Поля, которых не просили, не должны появиться
    assert "\"phone\"" not in result
    assert "\"cell\"" not in result
    assert "\"login\"" not in result


def test_gender_and_nationality_filters():
    """Фильтры по полу и национальности реально применяются API."""
    tool = RandomUserTool()
    result = tool.use(count=1, gender="female", nationality="fr")

    assert "female" in result.lower()
    assert "\"nat\": \"FR\"" in result or "\"nat\":\"FR\"" in result


def test_count_is_clamped_to_max_500():
    """count > 500 обрезается до 500."""
    tool = RandomUserTool()
    result = tool.use(count=10000)

    # Считаем количество объектов верхнего уровня по "gender"
    assert result.count("\"gender\"") == 500


def test_empty_or_invalid_input_does_not_crash():
    """Некорректные параметры не роняют инструмент."""
    tool = RandomUserTool()
    result = tool.use(count=0, gender="unknown", nationality="")

    # Даже при странных параметрах возвращается непустая строка
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Ошибка" not in result  # API всё равно отдаёт данные


def test_use_is_callable_with_no_args():
    """use() работает без аргументов (count=1 по умолчанию)."""
    tool = RandomUserTool()
    result = tool.use()

    assert result.strip().startswith("[")
    assert "full_name" in result