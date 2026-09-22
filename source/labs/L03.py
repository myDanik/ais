from build_labs import md, code, task

SPEC={'title':'TF-IDF, SVD и поиск по документам','cells':[
md('''### Протокол

Индексируем известную базу из 12 документов. Запросы и эталонные ответы не включаются в обучение представлений. Сравниваем два заранее заданных метода: TF-IDF и TF-IDF→SVD(6)→L2. Метрики: Recall@1, Recall@3, MRR@3, только для вопросов с эталонным документом. Вопросы без ответа рассматриваем отдельно. Сеть не нужна.'''),
code('''from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity

docs = pd.read_csv(DATA / "knowledge.csv", keep_default_na=False)
queries = pd.read_csv(DATA / "retrieval_queries.csv", keep_default_na=False)
content = docs["title"] + ". " + docs["text"]
doc_ids = docs["doc_id"].to_numpy()
assert docs["doc_id"].is_unique
assert not {"relevant_doc", "reference_answer"} & set(docs.columns)
print("Документов:", len(docs), "Вопросов:", len(queries))
display(docs[["doc_id", "title"]])'''),
task('1. Косинус вручную и в коде — 15 минут',
'''Реализуйте `cosine_safe(a,b)` для ненулевых векторов одинаковой размерности. Для нулевой нормы вызовите ValueError. Проверьте формулу на (1,0),(1,1),(0,1) и (10,10); объясните инвариантность к положительному масштабу.''',
'''def cosine_safe(a, b):
    # TODO: скалярное произведение и нормы; явная обработка нулевого вектора.
    raise NotImplementedError
''',
'''def cosine_safe(a, b):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("Нужны векторы одинаковой размерности")
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    if denominator == 0:
        raise ValueError("Косинус нулевого вектора не определён")
    return float(np.dot(a, b) / denominator)

for b in [(1, 1), (0, 1), (10, 10), (-1, 0)]:
    print(b, cosine_safe((1, 0), b))''',
'''assert np.isclose(cosine_safe([1, 0], [1, 1]), 1 / np.sqrt(2))
assert np.isclose(cosine_safe([1, 0], [10, 10]), cosine_safe([1, 0], [1, 1]))
try:
    cosine_safe([0, 0], [1, 0])
except ValueError:
    pass
else:
    raise AssertionError("Нужна явная обработка нулевого вектора")''',
'Результат 0.7071 — косинус, не вероятность правильности или синонимии. При отрицательном масштабе направление меняется.'),
task('2. Построить два индекса — 20 минут',
'''Обучите `vectorizer=TfidfVectorizer(ngram_range=(1,2), norm="l2")` только на content документов. Получите `X_docs`. Затем `TruncatedSVD(n_components=6, random_state=42)` и L2-нормировка дадут `Z_docs`. Выведите формы матриц и объясните, почему индексирование всех известных документов допустимо в этой постановке.''',
'''# TODO: обучите vectorizer и svd только на документах.
vectorizer = None
svd = None
X_docs = None
Z_docs = None
raise NotImplementedError''',
'''vectorizer = TfidfVectorizer(ngram_range=(1, 2), norm="l2")
X_docs = vectorizer.fit_transform(content)
svd = TruncatedSVD(n_components=6, random_state=42)
Z_docs = normalize(svd.fit_transform(X_docs))
print("TF-IDF:", X_docs.shape, "SVD:", Z_docs.shape)
print("Ненулевых элементов TF-IDF:", X_docs.nnz)
print("Нормы SVD:", np.linalg.norm(Z_docs, axis=1).round(6))''',
'''assert X_docs.shape[0] == len(docs)
assert Z_docs.shape == (len(docs), 6)
assert np.allclose(np.linalg.norm(Z_docs, axis=1), 1)
assert svd.components_.shape[1] == len(vectorizer.vocabulary_)''',
'База известна целиком; отложены запросы, а не документы. Знание текстов базы необходимо для индекса. Эталонные ответы и вопросы в fit не передаются.'),
task('3. Ранжирование и нулевой запрос — 20 минут',
'''Реализуйте `search(query, method="tfidf", k=3)`. Используйте тот же vectorizer и svd, никакого fit по запросу. Сортируйте по убыванию неокруглённой оценки, при равенстве — по doc_id. Верните DataFrame с doc_id, title, score. Для нулевого TF-IDF или SVD вектора возвращайте пустую таблицу с этими колонками.''',
'''def search(query, method="tfidf", k=3):
    # TODO: преобразование, проверка нуля, косинус, стабильная сортировка.
    raise NotImplementedError
''',
'''def search(query, method="tfidf", k=3):
    if method not in {"tfidf", "svd"} or not 1 <= k <= len(docs):
        raise ValueError("Проверьте метод и k")
    empty = pd.DataFrame(columns=["doc_id", "title", "score"])
    q = vectorizer.transform([query])
    if q.nnz == 0:
        return empty
    if method == "tfidf":
        scores = cosine_similarity(q, X_docs).ravel()
    else:
        z = svd.transform(q)
        if np.linalg.norm(z) < 1e-12:
            return empty
        scores = (normalize(z) @ Z_docs.T).ravel()
    result = docs[["doc_id", "title"]].assign(score=scores)
    return result.sort_values(["score", "doc_id"], ascending=[False, True], kind="stable").head(k).reset_index(drop=True)

for method in ["tfidf", "svd"]:
    print(method)
    display(search("Можно оставить учебник ещё на неделю?", method))
    display(search("щщщщщщщ", method))''',
'''for method in ["tfidf", "svd"]:
    r = search("Как продлить книгу?", method, 3)
    assert list(r.columns) == ["doc_id", "title", "score"]
    assert len(r) <= 3 and r["doc_id"].is_unique
    assert r["score"].is_monotonic_decreasing
    assert search("", method).empty
    assert search("щщщщщщщ", method).empty''',
'Короткий запрос с частично известными словами может дать ненулевой вектор, даже когда главная смысловая единица неизвестна. Не всякая слабая выдача связана с полностью нулевым запросом.'),
task('4. Оценка на отложенных вопросах — 20 минут',
'''Реализуйте `evaluate(part, method)` с Recall@1, Recall@3, MRR@3 и n_answerable. Только строки с непустым relevant_doc входят в среднее. При отсутствии эталона в top-3 вклад MRR@3 равен 0. Сравните оба заранее фиксированных метода на validation и test; не меняйте параметры после просмотра теста.''',
'''def evaluate(part, method):
    # TODO: фильтрация вопросов, ранги и средние.
    raise NotImplementedError

# TODO: создайте results_table.
raise NotImplementedError''',
'''def evaluate(part, method):
    answerable = part.loc[part["relevant_doc"].ne("")]
    if answerable.empty:
        raise ValueError("Нет ответимых вопросов для Recall")
    r1, r3, rr = [], [], []
    for row in answerable.itertuples():
        ranking = search(row.query, method, 3)["doc_id"].tolist()
        found = row.relevant_doc in ranking
        r1.append(bool(ranking) and ranking[0] == row.relevant_doc)
        r3.append(found)
        rr.append(1 / (ranking.index(row.relevant_doc) + 1) if found else 0)
    return {"recall_at_1": float(np.mean(r1)), "recall_at_3": float(np.mean(r3)),
            "mrr_at_3": float(np.mean(rr)), "n_answerable": len(answerable)}

rows = []
for split in ["validation", "test"]:
    for method in ["tfidf", "svd"]:
        rows.append({"split": split, "method": method,
                     **evaluate(queries[queries["split"].eq(split)], method)})
results_table = pd.DataFrame(rows)
display(results_table)
results_table.pivot(index="method", columns="split", values="recall_at_3").plot.bar(ylim=(0, 1), rot=0)
plt.ylabel("Recall@3"); plt.title("Попадание эталонного документа в top-3"); plt.tight_layout(); plt.show()
diagnostics = []
for row in queries[queries["relevant_doc"].ne("")].itertuples():
    a = search(row.query, "tfidf", 3)["doc_id"].tolist()
    b = search(row.query, "svd", 3)["doc_id"].tolist()
    if a != b:
        diagnostics.append({"query_id": row.query_id, "query": row.query,
                            "relevant_doc": row.relevant_doc, "tfidf": a, "svd": b})
print("Различающиеся выдачи:")
for row in diagnostics[:4]:
    print(row)''',
'''assert (results_table["recall_at_3"] >= results_table["recall_at_1"] - 1e-12).all()
assert results_table["mrr_at_3"].between(0, 1).all()
assert set(results_table["n_answerable"]) == {8, 16}
# Ручной мини-пример из лекции: ранги 1,3 и отсутствие в top-3.
assert np.isclose(np.mean([1, 1/3, 0]), 4/9)''',
'Ответимых вопросов 8 на validation и 16 на test. Шесть неответимых не включены как нули в Recall. Наблюдаемые различия на малом наборе не доказывают статистического превосходства.'),
code('''print("Вопросы без ответа в базе:")
for row in queries[queries["relevant_doc"].eq("")].itertuples():
    print(row.query)
    for method in ["tfidf", "svd"]:
        r = search(row.query, method, 1)
        print(method, r.to_dict("records"))'''),
md('''## 5. Интерпретация — 15 минут

Выберите два вопроса с разной выдачей методов и один без ответа. Прочитайте документы, объясните, где найден ответ и какие совпадения могли повлиять на ранжирование. Если выдачи совпали, возьмите собственную диагностическую перефразировку и явно назовите её дополнительным примером. Не подбирайте порог отказа по тесту.

**Мои выводы:** TODO.''', teacher='''## Эталон интерпретации

В проверенном запуске TF-IDF дал на валидации Recall@1=0,7500, Recall@3=0,8750, MRR@3=0,7917; SVD — 0,8750, 0,8750 и 0,8750. На тесте TF-IDF: 0,8750, 0,9375, 0,9063; SVD: 0,8750, 1,0000, 0,9167. Валидация содержит 8 ответимых вопросов, тест — 16. SVD увеличил тестовый Recall@3 на один вопрос из 16; это наблюдение на маленькой учебной базе, а не доказательство общего превосходства.

Фактические размерности: TF-IDF — 12×670, после SVD — 12×6. Разреженная исходная матрица содержит 816 ненулевых элементов. Нормы плотных строк после нормализации равны 1 с вычислительной погрешностью.

Конкретные разборы:

- Q01, «Как долго действует ссылка для смены пароля?»: у обоих методов D01 на первом месте, и документ действительно сообщает 30 минут. Остальные кандидаты различаются: у TF-IDF D04/D11, у SVD D02/D03. Здесь изменение соседей не меняет Recall@1 и не делает ответ более правильным.
- Q04, «Какие сведения нужны при технической ошибке?»: TF-IDF ставит D02 третьим после D05 и D01; SVD ставит D02 первым. В D02 перечислены название сервиса, время сбоя и код ошибки. Для этого вопроса Recall@3 обоих методов равен 1, но обратный ранг повышается с 1/3 до 1. Это конкретный пример того, зачем смотреть MRR, а не только попадание.
- «Сколько рублей составляет академическая стипендия?»: оба метода выбирают D11 о социальной стипендии, но сумма в базе отсутствует. У SVD косинус примерно 0,9909, что особенно ясно показывает: высокая близость не является уверенностью в наличии ответа. Нужны проверка содержимого и механизм отказа, которого в текущем поиске нет.

Сжатие до 6 координат не обязано улучшить каждый вопрос. Для диагноза различаем тематическую близость, точный факт и совпадение поверхностных слов. Вывод не основывается только на картинке пространства.

Для неответимого вопроса ближайший документ может существовать, даже если нужного факта нет. Например, сумма стипендии в базе не задана. Найденный документ об изменении реквизитов не становится источником суммы. Нулевой запрос обрабатывается отдельно; ненулевой неизвестный по смыслу запрос остаётся нерешённой задачей достаточности источника.

Документы и запросы используют один vectorizer и один svd. Независимое fit преобразования запроса разрушило бы совместимость. Косинус 0,8 не является вероятностью правильности; 2D-проекция сама по себе не подтверждает качество поиска.

Ответы защиты: косинус делит скалярное произведение на нормы, поэтому положительный масштаб сокращается; одинаковая размерность разных моделей не даёт совместимости; нулевой TF-IDF после линейного SVD остаётся нулевым; после SVD длина снова может отличаться от 1; у неответимого вопроса пустое множество релевантных документов, а не обычный пропущенный эталон. Перенос эталона с 3 на 2 увеличивает его вклад в MRR@3 с 1/3 до 1/2, но Recall@3 не меняется.'''),
]}
