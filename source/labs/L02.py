from build_labs import md, code, task

SPEC={'title':'TF-IDF и честная оценка классификатора','cells':[
md('''### Протокол

Сравниваем две заранее заданные конфигурации: слова (униграммы и биграммы) и `char_wb` (3–5 символов). Классификатор одинаковый. Выбор — по macro-F1 на validation, при равенстве выбираем words. Тест открываем после выбора; повторная настройка по нему запрещена в основном эксперименте. Данные синтетические, метрики не описывают реальный сервис.'''),
code('''from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report, ConfusionMatrixDisplay

df = pd.read_csv(DATA / "requests.csv", keep_default_na=False)
train = df[df["split"].eq("train")].copy()
valid = df[df["split"].eq("validation")].copy()
test = df[df["split"].eq("test")].copy()
labels = sorted(df["label"].unique())
print({k: len(v) for k, v in {"train": train, "validation": valid, "test": test}.items()})'''),
task('1. Проверить разделение — 10 минут',
'''Докажите кодом, что группы не пересекаются между частями, а все категории представлены. Сохраните множество групп каждой части в `groups`. Посмотрите распределение категорий, не обучая модель.''',
'''groups = {}
# TODO: заполните groups и проверьте непересечение.
raise NotImplementedError''',
'''parts = {"train": train, "validation": valid, "test": test}
groups = {name: set(part["group_id"]) for name, part in parts.items()}
assert groups["train"].isdisjoint(groups["validation"])
assert groups["train"].isdisjoint(groups["test"])
assert groups["validation"].isdisjoint(groups["test"])
for name, part in parts.items():
    assert set(part["label"]) == set(labels)
    print(name, part["label"].value_counts().to_dict())''',
'''assert set(groups) == {"train", "validation", "test"}
assert len(set.union(*groups.values())) == df["group_id"].nunique()''',
'Обучение содержит 72 группы, валидация 24 и тест 24. Стилистические варианты не перемешиваются. Фиксированный протокол не доказывает представительность синтетического корпуса.'),
task('2. Мини-пример TF-IDF — 10 минут',
'''Обучите `toy_vectorizer` на трёх строках из лекции. Выведите словарь, IDF и матрицу. Объясните, почему df слова «книга» равна 2, а не 3. Только эту маленькую матрицу можно преобразовать через `toarray()`.''',
'''toy = ["книга книга библиотека", "книга продление", "общежитие оплата"]
# TODO: создайте toy_vectorizer и toy_matrix.
raise NotImplementedError''',
'''toy = ["книга книга библиотека", "книга продление", "общежитие оплата"]
toy_vectorizer = TfidfVectorizer(smooth_idf=True, norm="l2", sublinear_tf=False)
toy_matrix = toy_vectorizer.fit_transform(toy)
print(toy_vectorizer.get_feature_names_out())
print("IDF:", toy_vectorizer.idf_.round(6))
display(pd.DataFrame(toy_matrix.toarray(), columns=toy_vectorizer.get_feature_names_out()))''',
'''assert toy_matrix.shape == (3, 5)
assert np.allclose(np.asarray(toy_matrix.multiply(toy_matrix).sum(axis=1)).ravel(), 1)
book_index = toy_vectorizer.vocabulary_["книга"]
assert np.isclose(toy_vectorizer.idf_[book_index], np.log(4 / 3) + 1)''',
'Первый вектор после L2: 0.549351, 0.835592, 0, 0, 0. Это веса, не вероятности по словам.'),
task('3. Базовая стратегия — 10 минут',
'''Обучите `DummyClassifier(strategy="most_frequent")` только на train. Вычислите accuracy и macro-F1 на validation, сохраните `baseline_scores`. Функция `score_predictions` должна всегда учитывать полный список меток и `zero_division=0`.''',
'''def score_predictions(y_true, y_pred):
    # TODO: словарь accuracy и macro_f1
    raise NotImplementedError

# TODO: обучите baseline и получите baseline_scores.
raise NotImplementedError''',
'''def score_predictions(y_true, y_pred):
    return {"accuracy": accuracy_score(y_true, y_pred),
            "macro_f1": f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)}

baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(np.zeros((len(train), 1)), train["label"])
baseline_pred = baseline.predict(np.zeros((len(valid), 1)))
baseline_scores = score_predictions(valid["label"], baseline_pred)
print(baseline_scores)''',
'''assert 0 <= baseline_scores["accuracy"] <= 1
assert 0 <= baseline_scores["macro_f1"] <= 1''',
'На равных 6 категориях accuracy 1/6, macro-F1 1/21. При равенстве частот конкретную постоянную метку определяет реализация; метрики симметричны.'),
task('4. Два конвейера и выбор — 20 минут',
'''Создайте два Pipeline: words с `TfidfVectorizer(ngram_range=(1,2), max_features=5000)` и chars с `TfidfVectorizer(analyzer="char_wb", ngram_range=(3,5), max_features=5000)`. В обоих — `LogisticRegression(C=1, max_iter=1000, random_state=42)`. Обучайте только на train. Сохраните `models`, `validation_scores`, `selected_name` и `selected`. Не используйте test на этом этапе.''',
'''models = {}
validation_scores = {}
# TODO: обучите оба варианта, оцените validation, выберите один.
raise NotImplementedError''',
'''models = {
    "words": Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
                       ("clf", LogisticRegression(C=1, max_iter=1000, random_state=42))]),
    "chars": Pipeline([("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), max_features=5000)),
                       ("clf", LogisticRegression(C=1, max_iter=1000, random_state=42))]),
}
validation_scores = {}
for name, model in models.items():
    model.fit(train["text"], train["label"])
    validation_scores[name] = score_predictions(valid["label"], model.predict(valid["text"]))
selected_name = "chars" if validation_scores["chars"]["macro_f1"] > validation_scores["words"]["macro_f1"] else "words"
selected = models[selected_name]
display(pd.DataFrame(validation_scores).T)
print("Выбран:", selected_name)''',
'''assert set(models) == {"words", "chars"}
assert selected_name in models
assert selected is models[selected_name]
assert all(0 <= s["macro_f1"] <= 1 for s in validation_scores.values())''',
'Веса и IDF обучаются внутри Pipeline на train. При равенстве выбран words. Дополнительное обучение train+validation не выполняется. Победитель не задан заранее: его определяет выполненный эксперимент.'),
task('5. Итоговая оценка, ошибки и контрольные входы — 30 минут',
'''Один раз примените выбранный конвейер к test. Вычислите `test_scores`, постройте матрицу ошибок (истина по строкам) и таблицу `errors`. Для разбора выберите до 5 ошибок из разных `group_id`. Если ошибок меньше, разберите все доступные и дополните анализ контрольными примерами, не изменяя модель.''',
'''# TODO: вычислите pred_test, test_scores и errors; постройте матрицу.
raise NotImplementedError''',
'''pred_test = selected.predict(test["text"])
test_scores = score_predictions(test["label"], pred_test)
print(test_scores)
print(classification_report(test["label"], pred_test, labels=labels, zero_division=0))
ConfusionMatrixDisplay.from_predictions(test["label"], pred_test, labels=labels, xticks_rotation=45, colorbar=False)
plt.title("Тест: истинные категории по строкам")
plt.tight_layout(); plt.show()
errors = test.assign(predicted=pred_test).loc[lambda x: x["label"].ne(x["predicted"])]
display(errors.drop_duplicates("group_id").head(5)[["group_id", "text", "label", "predicted"]])
control = ["", "жжжжжжжжж", "Не открывается виртуальная комната конференции"]
print(list(zip(control, selected.predict(control))))''',
'''assert len(pred_test) == len(test)
assert set(pred_test) <= set(labels)
assert len(errors) == int(np.sum(test["label"].to_numpy() != pred_test))''',
'Разбор тестовых ошибок после оценки допустим как диагностика, но не как основание для дальнейшего подбора с сохранением заявления о независимости того же теста. Нулевой вход может всё равно получить известный класс; это не содержательное распознавание.'),
md('''## Выводы и защита — 10 минут

Запишите выбранное представление, обе валидационные оценки, итоговые метрики, не менее трёх наблюдений об ошибках или контрольных примерах. Объясните, почему случайное разделение строк и обучение IDF на всём корпусе нарушили бы протокол. Не утверждайте, что результат переносится на реальные обращения без новой проверки.

**Мои выводы:** TODO.''', teacher='''## Эталон интерпретации

В проверенном запуске на закреплённом корпусе baseline получил accuracy=0,1667 и macro-F1=0,0476. На валидации words дал accuracy=0,4500 и macro-F1=0,4120; chars — accuracy=0,7417 и macro-F1=0,7430. Поэтому по заранее выбранному правилу победил chars. На тесте этого конвейера accuracy=0,7917, macro-F1=0,7652: неверно классифицированы 25 из 120 строк. Числа округлены до 4 знаков; точные значения находятся выше в выполненных ячейках. Превосходство относится к этим двум конфигурациям и этому синтетическому разбиению.

Конкретный разбор показанных ошибок:

- `library-19`: «Не могу найти монографию в списке доступной литературы» → ИТ вместо библиотеки. В тексте нет явного сбоя сервиса, речь о поиске издания. Гипотеза: общая конструкция «не могу» оказалась сильнее специфической библиотечной лексики. Для причинного подтверждения нужна отдельная проверка вкладов или минимальная пара.
- `library-20`: «Мне нужна помощь в подборе источников для курсовой» → ИТ. Это запрос библиографической помощи; слово «источники» не означает технический источник данных автоматически. Гипотеза: общие фрагменты просьбы о помощи и недостаток похожих примеров на train.
- `study-18`: «Когда откроется запись на повторный зачёт?» → ИТ. Вопрос о сроках учебной процедуры, техническая ошибка не заявлена. Это показывает ограничение маршрутизации по поверхностным фрагментам вроде «откроется» и «запись».
- `study-19`: «Как исправить ошибку в зачётной ведомости?» → ИТ. Здесь ошибка содержательная, в документе об оценке, а не сбой программы. Сходство с техническими обращениями — правдоподобная, но ещё не доказанная причина решения.
- `study-20`: «Где опубликован график экзаменационной сессии?» → поступление. Экзаменационная лексика встречается и у абитуриентов, но контекст «сессии» указывает на текущий учебный процесс. Модель не провела нужное различие в этой формулировке.

На тесте recall библиотеки=0,50, а учебного процесса=0,25. Поэтому общая accuracy≈0,79 не должна скрывать слабость этих категорий. Показанные строки относятся к разным базовым группам; остальные стилистические варианты не считаются независимыми кейсами.

Пять вариантов одной ошибки не считаются пятью независимыми кейсами. При анализе рассматриваются разные group_id. Частые причины путаницы проверяются чтением фактических строк: словесное совпадение другой темы, новая формулировка, недостаток контекста. Нельзя приписывать каждой ошибке одну причину без проверки.

В контрольном запуске пустая строка и «жжжжжжжжж» обе получили метку ИТ, как и содержательный запрос о виртуальной комнате конференции. Для первых двух это не успешное понимание: модель обязана выбирать известный класс и не содержит механизма отказа. Вход нужно проверять до классификатора. Обучение IDF по всем строкам использовало бы статистику теста; случайное разделение строк перемешало бы стилистические варианты.

Защита: объяснить одну координату TF-IDF, отличить fit от predict, восстановить precision/recall по матрице, указать, какое решение принято по validation. Важны воспроизводимость и корректная интерпретация, а не заранее обещанное числовое качество.'''),
]}
