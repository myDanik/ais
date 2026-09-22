from build_labs import md, code, task

SPEC={'title':'LLM: инструкции, декодирование и проверка ответа','cells':[
md('''### Подготовка и протокол

Нужна заранее загруженная `.cache/models/generator` (Qwen3-0.6B); можно указать общий `NLP_MODELS_DIR`. CPU, 4 потока, float32. Интернет при выполнении не используется. Модель небольшая: ошибки и отказы исследуются, а не скрываются.

Две инструкции × три вопроса в greedy; затем уточнённая инструкция, вопрос о сроке, T=0.5/1.0 при top_p=0.8, top_k=20, seed 7/42. Дополнительный JSON-запрос — greedy. Бюджет: 768 входных и 64 новых токена. Все ответы сохраняются без ручного редактирования.'''),
code('''import math
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed

torch.set_num_threads(4)
MODEL_ROOT = Path(os.environ.get("NLP_MODELS_DIR", ROOT / ".cache" / "models"))
MODEL_DIR = MODEL_ROOT / "generator"
if not (MODEL_DIR / "config.json").exists():
    raise FileNotFoundError("Сначала выполните scripts/prepare_models.py при доступном интернете")
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
model, loading_info = AutoModelForCausalLM.from_pretrained(MODEL_DIR, local_files_only=True,
    dtype=torch.float32, output_loading_info=True)
if loading_info["missing_keys"] or loading_info["mismatched_keys"] or loading_info["error_msgs"]:
    raise RuntimeError("Не удалось полностью загрузить веса генератора")
model.eval(); model.requires_grad_(False)
assert next(model.parameters()).device.type == "cpu"
MAX_INPUT, MAX_NEW = 768, 64
documents = pd.read_csv(DATA / "knowledge.csv", keep_default_na=False)
document = documents.loc[documents["doc_id"].eq("D03"), "text"].iloc[0]
questions = {
    "duration": "На сколько дней можно продлить книгу?",
    "reservation": "Можно ли продлить книгу, если её забронировал другой читатель?",
    "count": "Сколько раз за семестр можно продлевать книгу?",
}
print(document)
'''),
task('1. Temperature и nucleus на числах — 15 минут',
'''Реализуйте `temperature_probs(logits,T)` с T>0 и устойчивым softmax. `nucleus(probabilities,p)` возвращает массив исходной длины: оставляет минимальный верхний набор с накопленной массой≥p, остальные значения 0, оставшиеся нормирует. Используйте 0<p≤1. Создайте `temperature_table` для оценок (2,1,0) и T=0.5,1,2.''',
'''def temperature_probs(logits, T):
    # TODO: положительная T и softmax от logits/T.
    raise NotImplementedError

def nucleus(probabilities, p):
    # TODO: сортировка, накопленная масса и нормировка.
    raise NotImplementedError

# TODO: temperature_table.
raise NotImplementedError''',
'''def temperature_probs(logits, T):
    if T <= 0:
        raise ValueError("T должна быть положительной")
    z = np.asarray(logits, dtype=float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

def nucleus(probabilities, p):
    probabilities = np.asarray(probabilities, dtype=float)
    if not 0 < p <= 1 or probabilities.ndim != 1 or not len(probabilities):
        raise ValueError("Проверьте p и форму вероятностей")
    if (probabilities < 0).any() or not np.isclose(probabilities.sum(), 1):
        raise ValueError("Нужны неотрицательные нормированные вероятности")
    order = np.argsort(-probabilities, kind="stable")
    count = min(len(order), np.searchsorted(np.cumsum(probabilities[order]), p, side="left") + 1)
    out = np.zeros_like(probabilities)
    out[order[:count]] = probabilities[order[:count]]
    return out / out.sum()

temperature_table = pd.DataFrame([temperature_probs([2,1,0], T) for T in [0.5,1,2]],
                                 index=[0.5,1,2], columns=["token_A","token_B","token_C"])
display(temperature_table)
print("Nucleus:", nucleus([0.5,0.3,0.2], 0.75))
temperature_table.plot.bar(rot=0); plt.ylabel("Вероятность"); plt.xlabel("Temperature"); plt.tight_layout(); plt.show()''',
'''assert np.allclose(temperature_table.sum(axis=1), 1)
assert np.allclose(temperature_probs([2,1,0],1), [0.66524096,0.24472847,0.09003057])
assert np.allclose(nucleus([0.5,0.3,0.2],.75), [.625,.375,0])
try:
    temperature_probs([1,2],0)
except ValueError:
    pass
else:
    raise AssertionError("Greedy не реализуется делением на T=0")''',
'Числовой nucleus показывает определение. Реальная генерация дополнительно использует top_k = 20 и проверенный порядок операций библиотеки.'),
task('2. Шаблон и бюджет входа — 15 минут',
'''Реализуйте функцию `prepare_input(user_text)`, возвращающую (batch, input_length). System: «Ты учебный помощник. Отвечай по-русски». Второе сообщение user содержит user_text. Примените штатный chat template с tokenize=False, add_generation_prompt=True, enable_thinking=False. Токенизируйте с add_special_tokens=False, return_tensors="pt", без усечения. Пустой/нестроковый user_text и длина>MAX_INPUT вызывают ValueError. Сохранять строку rendered в batch не нужно: исходный user_text сохраняет оболочка ниже.''',
'''def prepare_input(user_text):
    # TODO: сообщения, chat template, tokenizer и проверка длины.
    raise NotImplementedError
''',
'''def prepare_input(user_text):
    if not isinstance(user_text, str) or not user_text.strip():
        raise ValueError("Нужен непустой пользовательский текст")
    messages = [{"role":"system", "content":"Ты учебный помощник. Отвечай по-русски"},
                {"role":"user", "content":user_text}]
    rendered = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    batch = tokenizer(rendered, add_special_tokens=False, return_tensors="pt")
    length = int(batch["input_ids"].shape[1])
    if length > MAX_INPUT:
        raise ValueError(f"Вход{length}токенов превышает бюджет{MAX_INPUT}")
    return batch, length

batch_example, length_example = prepare_input("Коротко объясни, что такое токен.")
print("Входных токенов:", length_example)
print(tokenizer.decode(batch_example["input_ids"][0]))''',
'''b, n = prepare_input("Короткий учебный вопрос")
assert b["input_ids"].shape == b["attention_mask"].shape and b["input_ids"].shape[1] == n
assert 0 < n <= MAX_INPUT
try:
    prepare_input("слово "*2000)
except ValueError:
    pass
else:
    raise AssertionError("Большой вход должен быть отклонён, не усечён молча")''',
'Общий system не содержит ограничения источника: это исследуемое различие между basic и strict в следующем задании. Режим thinking отключён для короткого опыта.'),
code('''# Готовая оболочка генерации сохраняет метаданные и выделяет только новые токены.
def generate_answer(user_text, mode="greedy", temperature=0.7, top_p=0.8, seed=42, max_new=64):
    if mode not in {"greedy","sample"} or not 1 <= max_new <= MAX_NEW:
        raise ValueError("Проверьте режим и лимит")
    if mode == "sample" and (temperature <= 0 or not 0 < top_p <= 1):
        raise ValueError("Некорректные параметры выборки")
    batch, length = prepare_input(user_text)
    if length + max_new > model.config.max_position_embeddings:
        raise ValueError("Превышено окно модели")
    kwargs = {"max_new_tokens":max_new, "do_sample":mode=="sample",
              "pad_token_id":tokenizer.eos_token_id, "use_cache":True}
    if mode == "sample":
        kwargs.update(temperature=temperature, top_p=top_p, top_k=20)
    set_seed(seed)
    started = time.perf_counter()
    with torch.inference_mode():
        output = model.generate(**batch, **kwargs)
    new_ids = output[0, length:]
    eos = model.generation_config.eos_token_id
    eos_ids = {eos} if isinstance(eos, int) else set(eos)
    stopped = "EOS" if len(new_ids) and int(new_ids[-1]) in eos_ids else ("limit" if len(new_ids)>=max_new else "other")
    return {"text":tokenizer.decode(new_ids, skip_special_tokens=True), "prompt":user_text,
            "input_tokens":length, "new_tokens":len(new_ids), "stop":stopped,
            "seconds":time.perf_counter()-started, "mode":mode,
            "temperature":temperature if mode=="sample" else None,
            "top_p":top_p if mode=="sample" else None, "top_k":20 if mode=="sample" else None, "seed":seed}
'''),
task('3. Две инструкции на трёх вопросах — 20 минут',
'''Создайте `build_prompt(question,variant)`, где variant равен basic или strict. Оба включают тот же document и question. Strict дополнительно требует только документ, одно короткое предложение и точную фразу «НЕТ ДАННЫХ» при отсутствии факта. Выполните 6 greedy-вызовов и сохраните список dict `prompt_records`; каждый содержит question_id, variant, question и все поля generate_answer. Таблица `prompt_results=pd.DataFrame(prompt_records)` показывает исходные ответы без очистки.''',
'''def build_prompt(question, variant):
    # TODO: два варианта с одинаковым источником и вопросом.
    raise NotImplementedError

prompt_records = []
# TODO: шесть greedy-вызовов и prompt_results.
raise NotImplementedError''',
'''def build_prompt(question, variant):
    if variant not in {"basic","strict"}:
        raise ValueError("Неизвестный вариант")
    instruction = "" if variant == "basic" else (
        "Используй только документ ниже. Ответь одним коротким предложением. "
        "Если нужного факта нет, ответь точно: НЕТ ДАННЫХ.\\n")
    return instruction + f"Документ:\\n{document}\\n Вопрос: {question}\\n Ответ:"

prompt_records = []
for variant in ["basic","strict"]:
    for question_id, question in questions.items():
        result = generate_answer(build_prompt(question, variant), mode="greedy")
        prompt_records.append({"question_id":question_id, "variant":variant, "question":question, **result})
        print(variant, question_id, result["stop"], repr(result["text"]))
prompt_results = pd.DataFrame(prompt_records)
display(prompt_results[["variant","question_id","input_tokens","new_tokens","stop"]])''',
'''assert len(prompt_records) == 6
assert set(prompt_results["variant"]) == {"basic","strict"}
assert set(prompt_results["question_id"]) == set(questions)
assert prompt_results["mode"].eq("greedy").all()
assert prompt_results["input_tokens"].le(MAX_INPUT).all() and prompt_results["new_tokens"].between(1, MAX_NEW).all()''',
'Ответимое duration: 14 дней; reservation: нельзя при брони; count: сведений нет. Фактическая правильность не assert-ится по обещанию модели; она оценивается отдельно.'),
task('4. Меняем декодирование — 15 минут',
'''Используйте один strict-промпт для questions["duration"]. При T=0.5 и 1.0 выполните sampling для seed 7 и 42, top_p=0.8, top_k=20 (в оболочке). Сохраните 4 dict в `decoding_records` и DataFrame `decoding_results`. Не выбирайте только самые разные ответы. Greedy-ориентир уже есть в prompt_results.''',
'''decoding_records = []
# TODO: четыре заранее запланированных вызова.
raise NotImplementedError''',
'''decoding_records = []
fixed_prompt = build_prompt(questions["duration"], "strict")
for T in [0.5,1.0]:
    for seed in [7,42]:
        result = generate_answer(fixed_prompt, mode="sample", temperature=T, top_p=.8, seed=seed)
        decoding_records.append(result)
        print("T", T,"seed", seed, result["stop"], repr(result["text"]))
decoding_results = pd.DataFrame(decoding_records)''',
'''assert len(decoding_records) == 4
assert set(zip(decoding_results["temperature"], decoding_results["seed"])) == {(0.5,7),(0.5,42),(1.0,7),(1.0,42)}
assert decoding_results["prompt"].nunique() == 1 and decoding_results["top_p"].eq(.8).all()''',
'Четыре наблюдения иллюстрируют механизм, но не доказывают статистическое превосходство T. Качество фактов проверяется независимо от разнообразия.'),
task('5. Строгий JSON-валидатор — 15 минут',
'''Реализуйте `validate_json_answer(text)` → dict с valid (bool), error (str), parsed (dict или None). Принимайте только исходный JSON-объект ровно с двумя ключами: answer (str) и has_answer (bool), без Markdown-ограждений. Ошибка возвращается в dict, не прерывает анализ. Выполните один greedy-запрос о 14 днях в JSON, сохраните `json_record` и `json_validation`. Это отдельный форматный опыт, а не третья версия основного сравнения.''',
'''def validate_json_answer(text):
    if not isinstance(text, str):
        return {"valid":False, "error":"Нужна строка", "parsed":None}
    # TODO: json.loads, корневойтип, ключи и типы значений.
    raise NotImplementedError

# TODO: json_record и json_validation.
raise NotImplementedError''',
'''def validate_json_answer(text):
    if not isinstance(text, str):
        return {"valid":False, "error":"Нужна строка", "parsed":None}
    try:
        obj = json.loads(text.strip())
    except (json.JSONDecodeError, TypeError) as e:
        return {"valid":False, "error":str(e), "parsed":None}
    if not isinstance(obj, dict) or set(obj) != {"answer","has_answer"}:
        return {"valid":False, "error":"Нужен объект с ровно answer и has_answer", "parsed":obj if isinstance(obj, dict) else None}
    if not isinstance(obj["answer"],str) or type(obj["has_answer"]) is not bool:
        return {"valid":False, "error":"Неверные типы", "parsed":obj}
    return {"valid":True, "error":"", "parsed":obj}

json_prompt = ("Ответь только по документу. Верни только JSON без Markdown, с ровно двумя полями: "
               "answer (строка), has_answer (логическое значение). "
               f"Документ: {document} Вопрос: {questions['duration']}")
json_record = generate_answer(json_prompt, mode="greedy")
json_validation = validate_json_answer(json_record["text"])
print("Исходный ответ:", repr(json_record["text"]), "Остановка:", json_record["stop"])
print(json_validation)''',
'''assert validate_json_answer('{"answer":"14 дней","has_answer":true}')["valid"]
assert not validate_json_answer('{"answer":"нет","has_answer":"false"}')["valid"]
assert not validate_json_answer('```json\\n{"answer":"14","has_answer":true}\\n```')["valid"]
assert not validate_json_answer('{"answer":')["valid"]
assert type(json_validation["valid"]) is bool''',
'Успех JSON-парсера не доказывает фактическую правильность. Валидатор не чинит автоматически ограждения/обрыв. Если модель нарушила формат, это полноценное наблюдение опыта.'),
code('''# Экспортируем исходные наблюдения, включая точные пользовательские промпты.
result_dir = ROOT / "outputs" / "L07"
result_dir.mkdir(parents=True, exist_ok=True)
records = {"system":"Ты учебный помощник. Отвечай по-русски", "checkpoint":"Qwen/Qwen3-0.6B",
           "prompt_runs":prompt_records, "decoding_runs":decoding_records,
           "json_run":json_record, "json_validation":json_validation}
(result_dir / "run_records.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
print("Исходные наблюдения сохранены:", result_dir / "run_records.json")'''),
md('''## 6. Таблица фактической оценки — 10 минут

Для 6 основных ответов заполните Markdown-таблицу: вариант/вопрос; главный факт 0–2; формат strict 0/1 (для basic — «не применимо»); неподдержанные утверждения; корректность отказа; комментарий с опорой на D03. Отдельно разберите 4 выборки и JSON. Учитывайте stop=limit: обрыв не равен осознанному ответу. Точные исходные наблюдения сохранены в outputs/L07/run_records.json.

**Моя таблица и выводы:** TODO.''', teacher='''## Эталон оценки фактического запуска

В проверенном запуске два промпта дали одинаково правильный срок, но не решили два других вопроса. Источник D03 разрешает продление на 14 дней и запрещает его при брони другим читателем; число продлений за семестр не задано.

| Вариант / вопрос | Исходный смысл ответа | Факты 0–2 | Формат strict | Оценка по источнику |
|---|---|---:|---|---|
| basic / duration | «На 14 дней» | 2 | не применимо | Срок подтверждён |
| basic / reservation | Разрешено даже при брони | 0 | не применимо | Противоречит условию D03 |
| basic / count | Рассуждение о продлении каждую неделю, обрыв | 0 | не применимо | Выдуманное правило, отказа нет, limit64 |
| strict / duration | «На 14 дней» | 2 | 1 | Срок подтверждён |
| strict / reservation | «Ответ: Можно» | 0 | 1 | Короткая форма соблюдена, факт неверен |
| strict / count | Вместо числа раз назван срок 14 дней | 0 | 0 | На вопрос не ответил, требуемого отказа нет |

Оценка strict/count не означает, что срок 14 дней ложный. Сам срок подтверждён, но не отвечает на вопрос о количестве продлений и подменяет требуемое признание отсутствия данных. В basic/count существенная неподдержанная деталь — возможность продления каждую неделю; её нельзя оправдать тем, что фраза содержит верное число 14.

При T=0.5/1.0 и seed 7/42 все четыре выборки на вопросе о сроке дали «14 дней» и EOS. На этом небольшом наборе изменение параметров не проявилось в тексте ответа. Это не опровергает математическое влияние temperature и не доказывает равенства настроек на всех запросах.

JSON-опыт в greedy вернул объект с answer строкой «14» и has_answer=true. Парсер, набор ключей и типы прошли проверку; число соответствует сроку из вопроса и источника. Отсутствие единицы внутри строки не нарушает заданную минимальную схему, поскольку вопрос спрашивает дни. Это один успешный форматный случай, не гарантия JSON для любого запроса.

Основные входы занимали 147–193 токена после шаблона. Basic/count остановился по 64 новым токенам; остальные основные ответы завершились EOS. Слишком длинный вход отклонён до генерации. Пустые маркеры think в распечатанном входном шаблоне относятся к формату Qwen3 при отключённом режиме, а не являются сгенерированным рассуждением.

Вывод: уточнение инструкции изменило форму части ошибок, но не исправило условие брони и вопрос без ответа в этом опыте. Проверка по источнику необходима. Никакие неудачные ответы не удалены и не дописаны вручную. Веса модели не обновлялись, источник оставался тем же; оценки относятся к закреплённому учебному запуску.

Ответы защиты: few-shot изменяет контекст, не веса; T должна быть положительной, greedy задаётся отдельным режимом; top-p берёт верхний набор до заданной массы и перенормирует; срез [0, L:] исключает вход; JSON-синтаксис не подтверждает факты; отсутствие сведений не равно 0 или отсутствию ограничений.'''),
]}
