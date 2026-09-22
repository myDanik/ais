from build_labs import md, code, task

SPEC={'title':'N-граммы, сглаживание и perplexity','cells':[
md('''### Фиксированный протокол

По одному обращению на группу: 72/24/24 текста. Один словарь, обученный только на train; min_count=2; EOS в целях, BOS только в истории. Сравниваем n=1,2,3 при alpha=0.1. Выбор по validation perplexity, при равенстве меньший n. На тесте оцениваем выбранную модель. Генерация ограничена 40 новыми предсказаниями.'''),
code('''from collections import Counter, defaultdict
import math

BOS, EOS, UNK = "<BOS>", "<EOS>", "<UNK>"
def tokenize(text):
    return re.findall(r"[а-яёa-z0-9]+", text.lower())

df = pd.read_csv(DATA / "requests.csv", keep_default_na=False).drop_duplicates("group_id")
parts = {name: [tokenize(t) for t in df.loc[df["split"].eq(name), "text"]]
         for name in ["train", "validation", "test"]}
assert tokenize("Студент читает книгу") == ["студент", "читает", "книгу"]
print({name: len(values) for name, values in parts.items()})

# Готовый итератор отделяет устройство истории от подсчёта частот.
def events(sentence, n):
    sequence = [BOS] * (n - 1) + list(sentence) + [EOS]
    for t in range(n - 1, len(sequence)):
        history = tuple(sequence[t - n + 1:t]) if n > 1 else ()
        yield history, sequence[t]
'''),
task('1. Общий словарь и UNK — 10 минут',
'''Посчитайте слова только в train. Сохраните слова с частотой≥2, добавьте EOS/UNK, исключите BOS. Создайте sorted-список `vocab` и отображённые последовательности `encoded`: неизвестные и редкие слова заменяются UNK одинаково во всех частях. Покажите долю UNK среди слов, без EOS.''',
'''# TODO: counts, vocab, encoded. Словарь нельзя строить по validation/test.
raise NotImplementedError''',
'''word_counts = Counter(t for sentence in parts["train"] for t in sentence)
known = {t for t, c in word_counts.items() if c >= 2}
vocab = sorted(known | {EOS, UNK})
encoded = {name: [[t if t in known else UNK for t in sentence] for sentence in sentences]
           for name, sentences in parts.items()}
print("Размер словаря:", len(vocab))
coverage = {}
for name, sentences in encoded.items():
    words = [t for sentence in sentences for t in sentence]
    coverage[name] = {"words": len(words), "unk_fraction": words.count(UNK) / len(words)}
print(json.dumps(coverage, ensure_ascii=False, indent=2))''',
'''assert BOS not in vocab and EOS in vocab and UNK in vocab
assert all(t in vocab for sentences in encoded.values() for sentence in sentences for t in sentence)
assert len(encoded["train"]) == 72 and len(encoded["validation"]) == len(encoded["test"]) == 24''',
'Доля UNK оценивает потерю различий словаря и считается без технического EOS. Для perplexity EOS будет включён в число целей.'),
task('2. Счётчики историй — 15 минут',
'''Реализуйте `fit_model(sentences,n,vocab)`, используя готовый events. Возвращайте словарь с n, vocab (tuple), counts (история→Counter продолжений) и totals (история→общее число продолжений). BOS не может быть выходной целью. Для каждой записи история начинается заново.''',
'''def fit_model(sentences, n, vocab):
    # TODO: отдельные счётчики для каждой истории.
    raise NotImplementedError
''',
'''def fit_model(sentences, n, vocab):
    if n < 1 or BOS in vocab or EOS not in vocab or UNK not in vocab:
        raise ValueError("Некорректный порядок или словарь")
    counts, totals = defaultdict(Counter), Counter()
    for sentence in sentences:
        for history, target in events(sentence, n):
            if target not in vocab:
                raise ValueError("Цель отсутствует в фиксированном словаре")
            counts[history][target] += 1
            totals[history] += 1
    return {"n": n, "vocab": tuple(vocab), "counts": dict(counts), "totals": totals}

toy_sentences = [tokenize(t) for t in ["студент читает книгу", "студент читает журнал", "студент возвращает книгу"]]
toy_vocab = sorted({t for s in toy_sentences for t in s} | {EOS, UNK})
toy_model = fit_model(toy_sentences, 2, toy_vocab)
print(toy_model["counts"][("студент",)])
print(toy_model["counts"][("читает",)])''',
'''toy_sentences = [tokenize(t) for t in ["студент читает книгу", "студент читает журнал", "студент возвращает книгу"]]
toy_vocab = sorted({t for s in toy_sentences for t in s} | {EOS, UNK})
toy_model = fit_model(toy_sentences, 2, toy_vocab)
assert len(toy_vocab) == 7
assert toy_model["counts"][("студент",)]["читает"] == 2
assert toy_model["totals"][("студент",)] == 3
assert sum(toy_model["totals"].values()) == 12  # 9 слов + 3EOS
assert all(BOS not in continuation for continuation in toy_model["counts"].values())''',
'Последний переход каждого предложения ведёт к EOS. У триграммы два начальных BOS образуют контекст первого слова, но не добавляют целей.'),
task('3. Сглаживание и нормировка — 15 минут',
'''Реализуйте `probability(model,history,target,alpha=0.1)` по add-alpha. Разрешено только alpha>0. Для неизвестной истории все счётчики равны 0. Функция `distribution` возвращает вероятности в порядке model["vocab"]. Проверьте мини-пример при alpha=1.''',
'''def probability(model, history, target, alpha=0.1):
    # TODO: числитель и знаменатель add-alpha.
    raise NotImplementedError

def distribution(model, history, alpha=0.1):
    return np.array([probability(model, history, t, alpha) for t in model["vocab"]])
''',
'''def probability(model, history, target, alpha=0.1):
    if alpha <= 0 or target not in model["vocab"]:
        raise ValueError("Нужно alpha>0 и цель из словаря")
    history = tuple(history)
    c = model["counts"].get(history, {}).get(target, 0)
    total = model["totals"].get(history, 0)
    return (c + alpha) / (total + alpha * len(model["vocab"]))

def distribution(model, history, alpha=0.1):
    return np.array([probability(model, history, t, alpha) for t in model["vocab"]])

print(dict(zip(toy_vocab, distribution(toy_model, ("студент",), alpha=1))))''',
'''assert np.isclose(probability(toy_model, ("студент",), "читает", 1), 0.3)
assert np.isclose(probability(toy_model, ("студент",), "возвращает", 1), 0.2)
for h in [(BOS,), ("студент",), ("невстречавшаяся_история",)]:
    p = distribution(toy_model, h, 1)
    assert (p > 0).all() and np.isclose(p.sum(), 1)
assert np.allclose(distribution(toy_model, ("невстречавшаяся_история",), 1), np.ones(7)/7)''',
'Невстречавшаяся история даёт равномерное распределение в выбранной простой модели. Это свойство add-alpha, а не универсальное свойство языка.'),
task('4. Perplexity и выбор порядка — 20 минут',
'''Реализуйте `evaluate_ppl`: сумма отрицательных ln вероятностей, число всех целей включая EOS, exp среднего. Пустой корпус должен вызывать ValueError; корпус с одним пустым предложением имеет одну цель EOS. Обучите n=1,2,3 на одном encoded["train"], оцените train/validation, выберите меньшую validation PPL (равенство→меньший n), затем оцените выбранную модель на test.''',
'''def evaluate_ppl(model, sentences, alpha=0.1):
    # TODO: nll, число целей и perplexity.
    raise NotImplementedError

# TODO: models, comparison, selected_n, selected, test_result.
raise NotImplementedError''',
'''def evaluate_ppl(model, sentences, alpha=0.1):
    nll, targets = 0.0, 0
    for sentence in sentences:
        for history, target in events(sentence, model["n"]):
            nll -= math.log(probability(model, history, target, alpha))
            targets += 1
    if targets == 0:
        raise ValueError("Корпус не содержит целевых позиций")
    return {"ppl": math.exp(nll/targets), "mean_nll": nll/targets, "targets": targets}

models = {n: fit_model(encoded["train"], n, vocab) for n in [1, 2, 3]}
rows = []
for n, model in models.items():
    a, b = evaluate_ppl(model, encoded["train"]), evaluate_ppl(model, encoded["validation"])
    rows.append({"n": n, "train_ppl": a["ppl"], "validation_ppl": b["ppl"],
                 "train_targets": a["targets"], "validation_targets": b["targets"]})
comparison = pd.DataFrame(rows)
selected_n = int(comparison.sort_values(["validation_ppl", "n"]).iloc[0]["n"])
selected = models[selected_n]
test_result = evaluate_ppl(selected, encoded["test"])
display(comparison)
print("Выбран n:", selected_n, "Тест:", test_result)
comparison.set_index("n")[["train_ppl", "validation_ppl"]].plot.bar(rot=0)
plt.ylabel("Perplexity, меньше лучше"); plt.tight_layout(); plt.show()''',
'''assert comparison["train_targets"].nunique() == comparison["validation_targets"].nunique() == 1
assert test_result["targets"] == sum(len(s)+1 for s in encoded["test"])
assert math.isfinite(test_result["ppl"]) and test_result["ppl"] >= 1
assert evaluate_ppl(selected, [[]])["targets"] == 1
assert np.isclose(math.exp(-np.log([0.5, 0.25, 0.5]).mean()), 16**(1/3))''',
'Нельзя усреднять perplexity документов вместо усреднения потерь по целям. Валидация выбирает только порядок; словарь и alpha не меняются.'),
task('5. Greedy и sampling — 20 минут',
'''Завершите `generate`: получите distribution по последним n−1 токенам, выберите максимум или rng.choice. EOS останавливает генерацию, иначе продолжайте до 40 новых предсказаний. Сохраните UNK. Результат: text, tokens (новые токены без EOS), stopped_by, steps (включая шаг EOS, если он был).''',
'''def generate(model, prefix="как", mode="sample", seed=42, max_new=40):
    # TODO: история, распределение, выбор, EOS и лимит.
    raise NotImplementedError
''',
'''def generate(model, prefix="как", mode="sample", seed=42, max_new=40):
    if mode not in {"greedy", "sample"} or max_new < 1:
        raise ValueError("Проверьте режим и лимит")
    rng = np.random.default_rng(seed)
    prefix_tokens = [t if t in known else UNK for t in tokenize(prefix)]
    history_tokens = [BOS]*(model["n"]-1) + prefix_tokens
    generated = []
    for step in range(max_new):
        history = tuple(history_tokens[-(model["n"]-1):]) if model["n"] > 1 else ()
        p = distribution(model, history)
        index = int(np.argmax(p)) if mode == "greedy" else int(rng.choice(len(p), p=p))
        token = model["vocab"][index]
        if token == EOS:
            return {"text": " ".join(prefix_tokens + generated), "tokens": generated,
                    "stopped_by": "EOS", "steps": step+1}
        generated.append(token); history_tokens.append(token)
    return {"text": " ".join(prefix_tokens + generated), "tokens": generated,
            "stopped_by": "limit", "steps": max_new}

generations = {"greedy": generate(selected, mode="greedy")}
for seed in [7, 42, 99]:
    generations[f"sample_{seed}"] = generate(selected, seed=seed)
for name, result in generations.items():
    print(name, result)''',
'''assert generate(selected, seed=42) == generate(selected, seed=42)
for result in [generate(selected, mode="greedy"), generate(selected, seed=7)]:
    assert 1 <= result["steps"] <= 40
    assert result["stopped_by"] in {"EOS", "limit"}
    assert all(t in vocab and t not in {BOS, EOS} for t in result["tokens"])
    if result["stopped_by"] == "limit": assert len(result["tokens"]) == 40''',
'Причина остановки является частью результата. Видимые UNK и странные переходы не удаляются ради красивой демонстрации. Одинаковый seed проверяет воспроизводимость, несколько seed — вариативность.'),
code('''# Скалярная RNN из лекции: параметры заданы вручную, обучение не выполняется.
h = 0.0
for x in [1.0, 0.0]:
    h = np.tanh(0.5*h + x)
    print("input", x, "state", h)'''),
md('''## 6. Выводы и защита — 5 минут

Назовите выбранный n и все измеренные показатели, объясните роль UNK и границ. Сравните хотя бы два сгенерированных продолжения, причины остановки и разницу условий оценки perplexity/генерации. Подробный отчёт завершите самостоятельно.

**Мои выводы:** TODO.''', teacher='''## Эталон интерпретации

В проверенном запуске словарь содержит 47 выходных элементов. Доля UNK среди исходных слов: train≈58,02%, validation≈68,48%, test≈71,08%. Такая высокая доля — существенное ограничение маленького корпуса: модель предсказывает сильно обобщённые последовательности, а не различает большинство исходных слов.

Измеренные perplexity: n=1 — train 9,6944, validation 6,6388; n=2 — train 5,2484, validation 4,9800; n=3 — train 5,0441, validation 6,0382. По заранее заданному правилу выбран n=2. На тесте его perplexity=4,9404, средняя отрицательная логарифмическая потеря=1,5975, число целей 190. Для train целей 527, для validation 189; порядок n этих чисел не меняет. Округления до 4 знаков, точные значения — в выводах ячеек.

Триграмма улучшила обучающую оценку относительно биграммы, но хуже на валидации. Это согласуется с ограниченной статистикой более длинных историй. Одновременно validation/test perplexity биграммы ниже обучающей: это не доказательство превосходного переноса, поскольку в отложенных текстах выше доля UNK и многие разные слова стали одной целью. Между порядками словарь фиксирован, но абсолютную величину нужно объяснять вместе с покрытием.

Фактическая генерация с префиксом «как»:

- Greedy выдал 40 маркеров UNK и остановился по лимиту. Это показывает доминирование неизвестного символа и зацикливание локального максимума, а не ошибку счётчика остановки.
- Sampling с seed 7: «как подать социальной стипендии», затем EOS на 4-м новом предсказании. Тема узнаваема, но конструкция грамматически неполна. Короткий удачный по теме фрагмент не доказывает общее качество.
- Seed 42 завершился EOS на 26-м шаге и смешал несколько конструкций с UNK; seed 99 — EOS на 31-м. Разнообразие увеличилось, но связность и различение редких слов не появились автоматически.

Оценка perplexity шла по эталонным историям; генерация использовала собственные выбранные токены. Поэтому нормальная вероятностная оценка совместима со странными свободными продолжениями. В отчёте сохраняются UNK и реальные причины остановки.

Скалярная RNN дала состояния 0,761594 и 0,363399. При втором входе 0 память ещё зависит от предыдущего 1; при двух нулевых входах оба состояния были бы 0. Параметры заданы вручную, никакого обучения нейросети в этом примере не было.

Ответы защиты: внутри шага альтернативы суммируются к 1; вдоль пути перемножаются условные вероятности. BOS задаёт контекст, EOS является предсказываемой границей. Add-alpha перераспределяет массу через общий знаменатель. Разные словари или токенизации задают разные события и числа целей. Greedy максимизирует только текущий шаг: в примере лекции 0,24 меньше 0,36. Все эти утверждения подтверждены мини-примерами и проверками выше.'''),
]}
