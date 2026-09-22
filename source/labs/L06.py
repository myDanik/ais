from build_labs import md, code, task

SPEC={'title':'Замороженный BERT-энкодер и классификация','cells':[
md('''### До занятия

Выполните `scripts/prepare_models.py` заранее. Нужна локальная папка `.cache/models/encoder` с закреплённым rubert-tiny2. Внешние API и GPU не используются. При общем преподавательском кеше можно задать `NLP_MODELS_DIR` с подпапками encoder/generator.

Сравниваем две фиксированные системы: char-TFIDF(3–5)+LogisticRegression(C=1) и нормированный CLS rubert-tiny2+такая же регрессия. Веса энкодера не изменяются. Тест используется для учебного сравнения заранее заданных систем, не для настройки.'''),
code('''import time
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, ConfusionMatrixDisplay, classification_report

torch.set_num_threads(4)
MODEL_ROOT = Path(os.environ.get("NLP_MODELS_DIR", ROOT / ".cache" / "models"))
MODEL_DIR = MODEL_ROOT / "encoder"
if not (MODEL_DIR / "config.json").exists():
    raise FileNotFoundError("Сначала выполните scripts/prepare_models.py при доступном интернете")
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
encoder, loading_info = AutoModel.from_pretrained(MODEL_DIR, local_files_only=True,
                                                 dtype=torch.float32, output_loading_info=True)
if loading_info["missing_keys"] or loading_info["mismatched_keys"] or loading_info["error_msgs"]:
    raise RuntimeError("Некорректная загрузка весов энкодера")
assert all(k.startswith("cls.") for k in loading_info["unexpected_keys"])
print("Неиспользованные головы предобучения:", sorted(loading_info["unexpected_keys"]))
encoder.eval(); encoder.requires_grad_(False)
print("Размерность:", encoder.config.hidden_size, "Слоёв:", encoder.config.num_hidden_layers)

df = pd.read_csv(DATA / "requests.csv", keep_default_na=False)
parts = {name: df[df["split"].eq(name)].copy() for name in ["train", "validation", "test"]}
labels = sorted(df["label"].unique())
'''),
task('1. Проверить токенизацию — 15 минут',
'''Создайте `token_batch` для трёх примеров с padding=True, truncation=True, max_length=128, return_tensors="pt". Выведите поля, формы, токены и маску. Убедитесь, что первая позиция — ожидаемый CLS, а не первое обычное слово. Сохраните полные длины всех обращений основного корпуса до усечения в массив `lengths`, а число значений больше 128 — в целочисленную переменную `truncated_count`.''',
'''examples = ["Как продлить книгу?", "Не работает личный кабинет.", "Спасибо"]
# TODO: token_batch, lengths и truncated_count.
raise NotImplementedError''',
'''examples = ["Как продлить книгу?", "Не работает личный кабинет.", "Спасибо"]
token_batch = tokenizer(examples, padding=True, truncation=True, max_length=128, return_tensors="pt")
print({k: tuple(v.shape) for k, v in token_batch.items()})
for ids, mask in zip(token_batch["input_ids"], token_batch["attention_mask"]):
    print(tokenizer.convert_ids_to_tokens(ids.tolist()))
    print("Маска:", mask.tolist())
lengths = np.array([len(ids) for ids in tokenizer(df["text"].tolist(), truncation=False)["input_ids"]])
truncated_count = int((lengths > 128).sum())
print("Полные длины min/max:", lengths.min(), lengths.max(), "Усечённых:", truncated_count)''',
'''assert token_batch["input_ids"].shape[0] == 3
assert token_batch["input_ids"].shape == token_batch["attention_mask"].shape
assert (token_batch["input_ids"][:,0] == tokenizer.cls_token_id).all()
assert len(lengths) == len(df) and 0 <= truncated_count <= len(df)''',
'Идентификаторы берутся из токенизатора, не подставляются из чужого BERT-примера. Неиспользованные cls.* головы допустимы при загрузке базового энкодера, missing encoder weights — нет.'),
task('2. Пакетное кодирование CLS — 20 минут',
'''Реализуйте `encode_texts(texts,batch_size=16)` на CPU: сохраните eval и inference_mode, токенизируйте пакет с теми же настройками, возьмите hidden[:,0,:], нормируйте по dim=1, объедините в исходном порядке. Пустой список возвращает массив (0,312), но пустые пользовательские обращения остаются отдельной проверкой данных. Сохраните `features` для трёх частей и время кодирования.''',
'''def encode_texts(texts, batch_size=16):
    # TODO: пакеты, маска, CLS, нормировка и конкатенация.
    raise NotImplementedError

# TODO: features и encode_seconds.
raise NotImplementedError''',
'''def encode_texts(texts, batch_size=16):
    texts = list(texts)
    if batch_size < 1 or not all(isinstance(t, str) for t in texts):
        raise ValueError("Нужен положительный batch_size и список строк")
    if not texts:
        return np.empty((0, encoder.config.hidden_size), dtype=np.float32)
    encoder.eval()
    chunks = []
    with torch.inference_mode():
        for start in range(0, len(texts), batch_size):
            batch = tokenizer(texts[start:start+batch_size], padding=True, truncation=True,
                              max_length=128, return_tensors="pt")
            hidden = encoder(**batch).last_hidden_state
            vector = torch.nn.functional.normalize(hidden[:,0,:], dim=1)
            chunks.append(vector.cpu().numpy())
    return np.concatenate(chunks, axis=0)

start_time = time.perf_counter()
features = {name: encode_texts(part["text"].tolist()) for name, part in parts.items()}
encode_seconds = time.perf_counter() - start_time
print({name: value.shape for name, value in features.items()})
print("Секунд кодирования:", encode_seconds)''',
'''for name, part in parts.items():
    assert features[name].shape == (len(part), 312)
    assert np.isfinite(features[name]).all()
    assert np.allclose(np.linalg.norm(features[name], axis=1), 1, atol=1e-5)
assert not encoder.training
assert all(not p.requires_grad for p in encoder.parameters())
assert encode_texts([]).shape == (0,312)''',
'Различайте отключённый dropout, замороженные параметры и отсутствие графа autograd. Все три явно заданы; sklearn получает только готовые numpy-массивы.'),
task('3. Повторяемость и pooling — 10 минут',
'''Сравните короткий текст отдельно и в пакете с длинным, используя encode_texts. Допуск максимальной разницы 1e-5. Затем на ручных H=[[1,0],[0,1],[9,9]], mask=[1,1,0] вычислите masked_mean и обычное среднее. Не заменяйте рекомендованный CLS в основной классификации этим мини-примером.''',
'''# TODO: batch_difference и masked_mean.
raise NotImplementedError''',
'''short = "Как продлить книгу?"
single = encode_texts([short])
paired = encode_texts([short, "Не могу войти в личный кабинет после смены пароля, появляется ошибка."])
repeat = encode_texts([short])
batch_difference = float(np.max(np.abs(single[0] - paired[0])))
print("Разница отдельного/пакетного:", batch_difference)
assert np.allclose(single, repeat, atol=1e-6)
H = np.array([[1.,0.],[0.,1.],[9.,9.]])
mask = np.array([1.,1.,0.])
masked_mean = (H * mask[:, None]).sum(axis=0) / mask.sum()
print("Обычное среднее:", H.mean(axis=0), "Masked mean:", masked_mean)''',
'''assert batch_difference < 1e-5
assert np.allclose(masked_mean, [0.5,0.5])''',
'Независимость от соседнего padding проверена численно. Masked mean показан только как пример другого pooling, а не как замена авторской рекомендации CLS.'),
task('4. Два фиксированных классификатора — 20 минут',
'''Обучите `embedding_clf=LogisticRegression(C=1,max_iter=1000,random_state=42)` на features["train"]. Классический `lexical` — Pipeline с char_wb(3,5), max_features=5000 и такой же регрессией. Оцените accuracy и macro-F1 по всем 6 меткам на validation/test. Конфигурации не меняются после просмотра чисел. `scores_table` содержит столбцы split, model, accuracy, macro_f1. `predictions` — словарь с ключами "tfidf" и "encoder" и массивами предсказаний теста. Постройте матрицу ошибок для encoder.''',
'''# TODO: embedding_clf, lexical, scores_table, predictions.
raise NotImplementedError''',
'''embedding_clf = LogisticRegression(C=1, max_iter=1000, random_state=42)
embedding_clf.fit(features["train"], parts["train"]["label"])
lexical = Pipeline([("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3,5), max_features=5000)),
                    ("clf", LogisticRegression(C=1, max_iter=1000, random_state=42))])
lexical.fit(parts["train"]["text"], parts["train"]["label"])
rows, predictions = [], {}
for split in ["validation", "test"]:
    pairs = {"tfidf": lexical.predict(parts[split]["text"]),
             "encoder": embedding_clf.predict(features[split])}
    for name, pred in pairs.items():
        rows.append({"split": split, "model": name,
                     "accuracy": accuracy_score(parts[split]["label"], pred),
                     "macro_f1": f1_score(parts[split]["label"], pred, labels=labels, average="macro", zero_division=0)})
        if split == "test": predictions[name] = pred
scores_table = pd.DataFrame(rows)
display(scores_table)
print(classification_report(parts["test"]["label"], predictions["encoder"], labels=labels, zero_division=0))
ConfusionMatrixDisplay.from_predictions(parts["test"]["label"], predictions["encoder"], labels=labels, xticks_rotation=45, colorbar=False)
plt.title("Замороженный энкодер: тест"); plt.tight_layout(); plt.show()''',
'''assert set(predictions) == {"tfidf", "encoder"}
assert all(len(p) == len(parts["test"]) for p in predictions.values())
assert scores_table["macro_f1"].between(0,1).all()
assert all(not p.requires_grad for p in encoder.parameters())''',
'Обе системы заранее зафиксированы. Тест не используется для выбора C, pooling или max_length. Это учебное повторное сравнение, не новый слепой benchmark.'),
task('5. Сопоставить ошибки — 10 минут',
'''Создайте `error_cases` для ВСЕХ тестовых строк с id, group_id, text, label, tfidf, encoder. Отбор интересных случаев выполняйте отдельно, не сокращая error_cases. Выведите до 5 разных групп: включите хотя бы одну ошибку энкодера и хотя бы одно улучшение относительно TF-IDF, если такие случаи существуют. Разберите конкретные формулировки, не утверждая причинность по одному совпавшему слову.''',
'''# TODO: error_cases и вывод разных групп.
raise NotImplementedError''',
'''error_cases = parts["test"].assign(tfidf=predictions["tfidf"], encoder=predictions["encoder"])
failures = error_cases[error_cases["encoder"].ne(error_cases["label"])].drop_duplicates("group_id").head(3)
improved = error_cases[error_cases["encoder"].eq(error_cases["label"]) & error_cases["tfidf"].ne(error_cases["label"])]
improved = improved[~improved["group_id"].isin(failures["group_id"])].drop_duplicates("group_id").head(2)
for row in pd.concat([failures, improved]).itertuples():
    print({"group": row.group_id, "text": row.text, "true": row.label, "tfidf": row.tfidf, "encoder": row.encoder})''',
'''assert len(error_cases) == len(parts["test"])
assert {"text","label","tfidf","encoder","group_id"} <= set(error_cases.columns)''',
'Отдельно назвать улучшения и сохраняющиеся ошибки. Разные стилистические варианты одной исходной просьбы не являются независимыми кейсами.'),
code('''# Длинный диагностический вход: важная просьба только в конце.
long_text = "Уточняю ранее отправленный вопрос. " * 80 + "Как продлить книгу?"
full_ids = tokenizer(long_text, truncation=False)["input_ids"]
cut_ids = tokenizer(long_text, truncation=True, max_length=128)["input_ids"]
cut_text = tokenizer.decode(cut_ids, skip_special_tokens=True)
print("Полная длина:", len(full_ids), "После усечения:", len(cut_ids))
print("Конец после усечения:", cut_text[-150:])
print("Слово 'книгу' сохранилось:", "книгу" in cut_text)
assert len(full_ids)>128 and len(cut_ids)==128 and "книгу" not in cut_text
'''),
md('''## 6. Длина, BIO и выводы — 15 минут

Первые 5 минут — разбор усечения; следующие 5 — вручную присвоить BIO-метки словам «Анна Петрова учится в университете Север», включая оба слова организации; последние 5 — итоговый вывод по метрикам и ограничениям.

**BIO:** TODO.

**Мои выводы:** TODO.''', teacher='''## Эталон интерпретации

В проверенном запуске ни одно из 600 основных обращений не усечено: полная длина со специальными токенами от 8 до 21. Формы признаков: train 360×312, validation 120×312, test 120×312. Разница кодирования короткой строки отдельно и в пакете порядка 10⁻⁷, существенно меньше допуска 10⁻⁵. Все веса энкодера заморожены, dropout отключён.

Валидация: TF-IDF accuracy=0,7417, macro-F1=0,7430; энкодер accuracy=0,8000, macro-F1=0,7893. Тест: TF-IDF 0,7917/0,7652; энкодер 0,9000/0,8863. В этом конкретном опыте готовые признаки лучше по общим метрикам, но recall класса admission только 0,40: 12 из 20 строк поступления отнесены к другим категориям. Общая accuracy 0,90 не должна скрывать эту слабость. Точные значения приведены в выполненных ячейках.

Конкретные случаи:

- `admission-17`, изменение направления в заявлении абитуриента: TF-IDF верен, энкодер выбирает study. В тексте есть указание на абитуриента; ошибка показывает, что тематическая близость к учебному процессу не гарантирует правильную организационную метку. Влияние отдельных слов — гипотеза, а не доказанная причина.
- `admission-19`, показанный вариант с «Здравствуйте!» о почтовой отправке пакета документов: по авторской метке это admission, энкодер выбирает library. Сама короткая фраза без контекста неоднозначна и могла бы относиться к разным подразделениям. Поэтому это одновременно расхождение с меткой и повод проверить достаточность данных разметки, а не доказательство бессмысленности модели.
- `admission-20`, консультация по вступительному собеседованию: TF-IDF верен, энкодер выбирает study. Контекст поступления не оказался достаточным для этой фиксированной головы.
- `library-19`, поиск монографии, и `library-20`, подбор источников для курсовой: TF-IDF ошибочно выбирает it, энкодер правильно выбирает library. Это конкретные улучшения на двух разных группах, а не основание объявлять универсальное превосходство BERT.

Длинный диагностический текст имел 566 токенов, после ограничения осталось 128. Просьба с «книгу» в конце исчезла. Классификатор не может использовать фрагмент, которого нет на входе; для длинных документов нужна отдельная стратегия.

Ручное среднее по всем трём векторам было (3,3333;3,3333), masked mean — (0,5;0,5). Этот пример объясняет исключение padding, но основная модель использует рекомендованный нормированный CLS, а не mean pooling.

BIO: B-PER, I-PER, O, O, B-ORG, I-ORG. Это ручная разметка по заданной политике, не результат предсказания rubert-tiny2. Новая логистическая голова обучена по train. Ответы защиты: eval меняет режим модулей, не сам признак обучаемости; CLS выбран по карточке конкретной модели; фиксированный инференс не извлекает статистику корпуса как fit TF-IDF; влияние соседнего padding требует проверки маски и pooling; случайная NER-голова не обучена распознавать сущности; исчезновение конца доказывает потерю входной информации, а не непонимание сохранённого текста.'''),
]}
