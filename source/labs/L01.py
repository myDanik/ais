from build_labs import md, code, task

SPEC={'title':'Аудит и подготовка текстового корпуса','cells':[
md('''### Результаты работы

Составить паспорт данных; найти пустоты, повторы и конфликтные метки; реализовать минимальную нормализацию; сравнить токенизацию; показать потери смысла. Подробный порядок и критерии — в `lab_guide.pdf`.

Ноутбук содержит намеренно незавершённые функции. `NotImplementedError` в TODO — ожидаемая остановка до выполнения задания. Запускайте ячейки последовательно.'''),
code('''requests = pd.read_csv(DATA / "requests.csv", keep_default_na=False)
audit = pd.read_csv(DATA / "audit_requests.csv", keep_default_na=False)
manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
required = {"id", "text", "label", "group_id", "split"}
assert required <= set(requests.columns), "Неверная схема основного корпуса"
assert required <= set(audit.columns), "Неверная схема файла аудита"
print("Основной корпус:", requests.shape)
print("Аудит:", audit.shape)
display(audit.head())'''),
task('1. Паспорт и первичный аудит — 15 минут',
'''Создайте `summary`: число записей и групп основного корпуса, распределение меток, число содержательно пустых строк аудита и список неизвестных меток. Пустыми считайте строки, которые после `strip()` не содержат символов. Допустимые метки возьмите из `manifest["labels"]`.''',
'''# TODO: вычислите показатели из таблиц, не записывайте числа вручную.
summary = {}
raise NotImplementedError("Заполните summary")''',
'''empty = audit["text"].str.strip().eq("")
unknown = ~audit["label"].isin(manifest["labels"])
summary = {
    "rows": len(requests),
    "groups": requests["group_id"].nunique(),
    "labels": requests["label"].value_counts().to_dict(),
    "empty_rows": int(empty.sum()),
    "unknown_labels": sorted(audit.loc[unknown, "label"].unique().tolist()),
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
display(audit.loc[empty | unknown])''',
'''assert summary["rows"] == len(requests)
assert sum(summary["labels"].values()) == len(requests)
assert isinstance(summary["empty_rows"], int)''',
'Ожидаются 600 записей, 120 групп, 100 записей каждой из 6 категорий, 2 пустые строки и unknown. Числа проверяются выполнением, а не сообщаются как заранее полученное качество модели.'),
task('2. Минимальная нормализация — 15 минут',
'''Реализуйте `normalize_text`: принимает только `str`, иначе `TypeError`; NFC; сжатие пробельных последовательностей в один пробел; удаление крайних пробелов. Сохраните оригинал и создайте колонку `normalized`. Нельзя удалять отрицания, цифры, регистр и пунктуацию.''',
'''def normalize_text(text):
    # TODO: реализуйте согласованную политику.
    raise NotImplementedError

original = audit["text"].copy()
audit["normalized"] = audit["text"].map(normalize_text)''',
'''def normalize_text(text):
    if not isinstance(text, str):
        raise TypeError("Ожидалась строка")
    return re.sub(r"\\s+", " ", unicodedata.normalize("NFC", text)).strip()

original = audit["text"].copy()
audit["normalized"] = audit["text"].map(normalize_text)
display(audit.loc[audit["text"].ne(audit["normalized"]), ["id", "text", "normalized"]])''',
'''for value in ["  Не  отменяйте!  ", "Ошибка 403", "и\\u0306", ""]:
    result = normalize_text(value)
    assert normalize_text(result) == result  # идемпотентность
assert normalize_text("  Не  отменяйте!  ") == "Не отменяйте!"
assert normalize_text("Ошибка 403") == "Ошибка 403"
assert normalize_text("и\\u0306") == "й"
assert audit["text"].equals(original)
try:
    normalize_text(None)
except TypeError:
    pass
else:
    raise AssertionError("Нестрочный вход должен вызывать TypeError")''',
'Политика ограничена однострочными обращениями. Сжатие пробелов нельзя переносить без проверки на стихи, код или таблицы.'),
task('3. Повторы и конфликтные метки — 15 минут',
'''Среди непустых нормализованных текстов найдите все строки с повторяющимся текстом (`duplicate_rows`) и тексты с несколькими метками (`conflicts`). Не удаляйте их автоматически. Укажите, какие записи требуют решения разметчика.''',
'''# TODO: исключите пустые тексты и найдите повторы и конфликты.
duplicate_rows = None
conflicts = None
raise NotImplementedError''',
'''nonempty = audit.loc[audit["normalized"].ne("")].copy()
duplicate_rows = nonempty.loc[nonempty.duplicated("normalized", keep=False)]
label_counts = nonempty.groupby("normalized")["label"].nunique()
conflicts = label_counts[label_counts > 1]
display(duplicate_rows[["id", "normalized", "label"]])
print("Конфликтные тексты:")
display(conflicts)''',
    '''assert not duplicate_rows["normalized"].eq("").any()
assert {"it-01-1", "audit-duplicate", "audit-conflict"} <= set(duplicate_rows["id"])
assert len(conflicts) > 0 and (conflicts > 1).all()''',
'Три записи относятся к одному нормализованному тексту; две метки образуют один конфликт. Дополнительно вручную обнаруживается audit-label: книга ошибочно размечена как общежитие. Решение фиксируется в отчёте, корпус не переписывается.'),
task('4. Токены и словарь — 15 минут',
'''Для каждой строки сравните `split()` и `re.findall(r"\\w+|[^\\w\\s]", text)`. Создайте таблицу `token_report` с исходным текстом, списками токенов и их количеством. Объясните разбиение адреса электронной почты.''',
'''examples = ["ИТ-поддержка: вход не работает!",
            "Письмо: help@sever.example, ошибка 403",
            "книга книга журнал"]
# TODO: создайте token_report.
raise NotImplementedError''',
'''examples = ["ИТ-поддержка: вход не работает!",
            "Письмо: help@sever.example, ошибка 403",
            "книга книга журнал"]
rows = []
for text in examples:
    a = text.split()
    b = re.findall(r"\\w+|[^\\w\\s]", text)
    rows.append({"text": text, "split": a, "regex": b,
                 "n_split": len(a), "n_regex": len(b), "vocab_regex": len(set(b))})
token_report = pd.DataFrame(rows)
display(token_report)''',
'''assert len(token_report) == len(examples)
assert all(len(tokens) == n for tokens, n in zip(token_report["regex"], token_report["n_regex"]))''',
'В первой строке 4 и 8 токенов, в третьей 3 вхождения и 2 разных токена. Regex разбивает адрес на части: это выбранное правило, а не обнаружение почтовой сущности.'),
task('5. Потеря смысла — 10 минут',
'''Напишите `aggressive`: нижний регистр, словесные токены, удаление «я» и «не», удаление чисто цифровых токенов. Сравните два отзыва и сообщение с кодом ошибки. Это намеренно плохой конвейер для некоторых задач, не рекомендация к применению.''',
'''def aggressive(text):
    # TODO: реализуйте именно заданный экспериментальный вариант.
    raise NotImplementedError

texts = ["Я доволен работой портала", "Я не доволен работой портала", "Ошибка 403"]
for text in texts:
    print(text, "=>", aggressive(text))''',
'''def aggressive(text):
    tokens = re.findall(r"\\w+", text.lower())
    return " ".join(t for t in tokens if t not in {"я", "не"} and not t.isdigit())

texts = ["Я доволен работой портала", "Я не доволен работой портала", "Ошибка 403"]
for text in texts:
    print(text, "=>", aggressive(text))''',
'''assert aggressive(texts[0]) == aggressive(texts[1])
assert "403" not in aggressive(texts[2])''',
'Совпадение представлений — доказанная потеря различия в этих примерах. Оно не означает, что любое удаление стоп-слов всегда ухудшает тематическую классификацию.'),
code('''# Ограниченный учебный словарь: демонстрирует неоднозначность, не заменяет анализатор.
lemma_candidates = {"книги": ["книга"], "книгой": ["книга"], "стали": ["сталь", "стать"]}
for token, candidates in lemma_candidates.items():
    print(token, "=>", candidates)
print("Разберите по контексту: Образцы стали / Студенты стали проверять")'''),
md('''## 6. Выводы и защита — 10 минут

Впишите в Markdown ниже: три обнаруженных дефекта; решение по конфликту меток; два случая потери смысла; почему корпус синтетический и почему 500/600 строк не равно стольким же независимым ситуациям. Подготовьте собственную контрольную строку.

**Мои выводы:** TODO.

Перед сдачей перезапустите ядро и выполните весь ноутбук. Прикрепите отчёт с паспортом, политикой обработки, найденными дефектами и выводами. Не изменяйте исходные CSV.''', teacher='''## 6. Эталон выводов и защита

В файле аудита обнаружены две содержательно пустые строки, неизвестная метка `unknown`, три записи одного нормализованного текста и один конфликт по этому тексту. Запись `audit-label` о продлении книги ошибочно направлена в общежитие. Для спорных случаев требуется проверка инструкции; исходный файл в работе сохраняется.

Удаление «не» делает противоположные отзывы одинаковыми; удаление 403 лишает сообщение диагностического кода. NFC согласует канонически эквивалентные записи, но не исправляет смешение алфавитов. `split` сохраняет приклеенную пунктуацию; regex отделяет знаки, включая части адреса электронной почты.

600 записей отражают 120 базовых обращений, по 5 стилистических вариантов. Метрики следующих работ характеризуют этот учебный корпус и не доказывают перенос на реальную приёмную.

Контрольная строка защиты: `  Не  отменяйте запись на 12 октября! `. После нормализации: `Не отменяйте запись на 12 октября!`. Сохраняются отрицание, дата, регистр и восклицательный знак. Повторный вызов результата не меняет.

По морфологии: «Образцы стали» → сталь; «Студенты стали проверять» → стать. Выбор сделан по контексту, сам учебный словарь кандидатов его не выполняет.

Ответы защиты: строка может быть вариантом исходной ситуации; NFC не выполняет замену алфавитов; частотное слово и число могут определять смысл; конфликт нельзя скрывать случайным выбором; идемпотентность гарантирует стабильность повторного применения, но не полезность преобразования для задачи.'''),
]}
