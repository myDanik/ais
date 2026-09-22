from build_labs import md, code, task

SPEC={'title':'Attention, маски и проверка причинности','cells':[
md('''### Что реализуем

Одна голова scaled dot-product attention в NumPy. Q/K/V заданы вручную; это проверка математического механизма, а не обученная модель русского языка. True в нашей маске означает «разрешено». Задачи: устойчивый softmax, правильная ось, causal/padding маски, отсутствие влияния будущего и проверка позиционного сигнала.'''),
task('1. Устойчивый softmax — 10 минут',
'''Реализуйте `softmax_rows(scores)` для двумерной матрицы. Нормируйте каждую строку, предварительно вычитая её максимум. Разрешён −inf для закрытых ключей; NaN, +inf и строка из одних −inf должны вызывать ValueError. Не применять одну нормировку ко всей матрице.''',
'''def softmax_rows(scores):
    # TODO: проверки, максимум строки, экспонента и сумма по оси ключей.
    raise NotImplementedError
''',
'''def softmax_rows(scores):
    scores = np.asarray(scores, dtype=float)
    if scores.ndim != 2 or min(scores.shape) == 0:
        raise ValueError("Нужна непустая двумерная матрица")
    if np.isnan(scores).any() or np.isposinf(scores).any() or np.isneginf(scores).all(axis=1).any():
        raise ValueError("Недопустимые оценки или полностью закрытая строка")
    shifted = scores - scores.max(axis=1, keepdims=True)
    exponents = np.exp(shifted)
    return exponents / exponents.sum(axis=1, keepdims=True)

print(softmax_rows([[1000, 1001, 1002], [-2, 0, 1]]))''',
'''scores = np.array([[1000., 1001., 1002.], [-2., 0., 1.]])
p = softmax_rows(scores)
assert np.isfinite(p).all() and np.allclose(p.sum(axis=1), 1)
assert np.allclose(p, softmax_rows(scores + 10000))
assert not np.isclose(p.sum(), 1)  # здесь две отдельные строки-распределения
try:
    softmax_rows([[-np.inf, -np.inf]])
except ValueError:
    pass
else:
    raise AssertionError("Полностью закрытая строка должна быть отклонена")''',
'Вычитание максимума делает большие конечные оценки безопасными для экспоненты. Проверка двух разных строк ловит неверную общую нормировку.'),
task('2. Одна голова attention — 20 минут',
'''Реализуйте `attention(Q,K,V,allow=None)`: оценки Q@K.T/√d_k, затем маска через −inf, softmax_rows, выход A@V. Верните (output, weights). Готовые проверки размерностей можно сохранить. Маска должна быть bool формы (n_queries, n_keys), в каждой строке хотя бы один True.''',
'''def attention(Q, K, V, allow=None):
    Q, K, V = [np.asarray(x, dtype=float) for x in [Q, K, V]]
    if any(x.ndim != 2 or min(x.shape) == 0 for x in [Q, K, V]):
        raise ValueError("Нужны непустые матрицы")
    if Q.shape[1] != K.shape[1] or K.shape[0] != V.shape[0]:
        raise ValueError("Несогласованные размерности")
    if not all(np.isfinite(x).all() for x in [Q, K, V]):
        raise ValueError("Входы должны быть конечными")
    if allow is None:
        allow = np.ones((len(Q), len(K)), dtype=bool)
    allow = np.asarray(allow)
    if allow.dtype != bool or allow.shape != (len(Q), len(K)) or not allow.any(axis=1).all():
        raise ValueError("Некорректная маска")
    # TODO: scores, masked_scores, weights, output.
    raise NotImplementedError
''',
'''def attention(Q, K, V, allow=None):
    Q, K, V = [np.asarray(x, dtype=float) for x in [Q, K, V]]
    if any(x.ndim != 2 or min(x.shape) == 0 for x in [Q, K, V]):
        raise ValueError("Нужны непустые матрицы")
    if Q.shape[1] != K.shape[1] or K.shape[0] != V.shape[0]:
        raise ValueError("Несогласованные размерности")
    if not all(np.isfinite(x).all() for x in [Q, K, V]):
        raise ValueError("Входы должны быть конечными")
    if allow is None:
        allow = np.ones((len(Q), len(K)), dtype=bool)
    allow = np.asarray(allow)
    if allow.dtype != bool or allow.shape != (len(Q), len(K)) or not allow.any(axis=1).all():
        raise ValueError("Некорректная маска")
    scores = Q @ K.T / np.sqrt(Q.shape[1])
    weights = softmax_rows(np.where(allow, scores, -np.inf))
    return weights @ V, weights

Q = K = np.eye(2)
V = np.array([[10., 0.], [0., 20.]])
output, weights = attention(Q, K, V)
print("Веса:", weights)
print("Выход:", output)''',
'''Q = K = np.eye(2)
V = np.array([[10., 0.], [0., 20.]])
output, weights = attention(Q, K, V)
assert np.allclose(weights[0], [0.66976155, 0.33023845])
assert np.allclose(output[0], [6.69761549, 6.60476901])
# Несимметричный cross-пример: два запроса, три ключа, два признака значений.
o, a = attention([[1, 0], [1, 1]], [[1, 0], [0, 1], [2, -1]], [[1, 2], [3, 4], [5, 6]])
assert o.shape == (2, 2) and a.shape == (2, 3)
assert np.allclose(a.sum(axis=1), 1)''',
'Размер d_k берётся из признаковой оси Q, не из числа токенов. Несимметричный пример нужен, потому что на симметричной матрице некоторые ошибки оси незаметны.'),
task('3. Causal-маска и изменение будущего — 20 минут',
'''Создайте нижнетреугольную булеву маску, включая диагональ. Сравните пример 2×2 с маской и без, сохранив `masked_output` и `masked_weights`. Матрица `X` из трёх строк и `mask3` заданы ниже и понадобятся также в заданиях 4–5. Создайте `V_changed=X.copy()` и прибавьте к строке 2 вектор (100;−50). Проверьте, что первые два выхода с causal-маской не изменились, а без маски изменение влияет на более ранние выходы.''',
'''causal = np.tril(np.ones((2, 2), dtype=bool))
X = np.array([[1., 0.], [0., 1.], [1., 1.]])
mask3 = np.tril(np.ones((3, 3), dtype=bool))
# TODO: masked_output, masked_weights; V_changed и сравнение выходов.
raise NotImplementedError''',
'''causal = np.tril(np.ones((2, 2), dtype=bool))
masked_output, masked_weights = attention(Q, K, V, causal)
print("Causal-веса:", masked_weights)
print("Causal-выход:", masked_output)

X = np.array([[1., 0.], [0., 1.], [1., 1.]])
V_changed = X.copy(); V_changed[2] += [100., -50.]
mask3 = np.tril(np.ones((3, 3), dtype=bool))
before, _ = attention(X, X, X, mask3)
after, _ = attention(X, X, V_changed, mask3)
open_before, _ = attention(X, X, X)
open_after, _ = attention(X, X, V_changed)
print("Максимальное изменение ранних causal-выходов:", np.max(np.abs(before[:2] - after[:2])))
print("Максимальное изменение без маски:", np.max(np.abs(open_before[:2] - open_after[:2])))
assert np.allclose(before[:2], after[:2])
assert not np.allclose(open_before[:2], open_after[:2])

fig, axes = plt.subplots(1, 2, figsize=(8, 3))
for ax, matrix, title in zip(axes, [weights, masked_weights], ["Без маски", "Causal"]):
    ax.imshow(matrix, vmin=0, vmax=1, cmap="YlGnBu")
    for i in range(2):
        for j in range(2): ax.text(j, i, f"{matrix[i, j]:.3f}", ha="center", va="center")
    ax.set_title(title); ax.set_xlabel("Ключ"); ax.set_ylabel("Запрос")
    ax.set_xticks([0,1]); ax.set_yticks([0,1])
plt.tight_layout(); plt.show()''',
'''assert np.allclose(masked_weights[0], [1, 0])
assert np.allclose(masked_output[0], [10, 0])
assert np.allclose(masked_output[1], output[1])
assert np.all(masked_weights[~causal] == 0)''',
'Проверка изменяет значения будущей позиции при неизменных Q/K. Это изолированный тест запрета передачи информации. Тепловая карта иллюстрирует уже проверенные числа.'),
task('4. Padding и закрытая строка — 10 минут',
'''Последний ключ трёхпозиционного X считайте padding. Постройте padding_allow для всех запросов, затем совместите с mask3 через AND. Проверьте нулевые веса последнего столбца. Покажите, что attention со строкой без доступного ключа вызывает ValueError, а замена запрещённой оценки на 0 до softmax не даёт нулевой вероятности.''',
'''# TODO: padding_allow, combined, padding_weights и контрпример маскирования нулём.
raise NotImplementedError''',
'''padding_allow = np.broadcast_to(np.array([True, True, False]), (3, 3)).copy()
combined = padding_allow & mask3
padding_output, padding_weights = attention(X, X, X, combined)
assert np.all(padding_weights[:, 2] == 0)
print("Совмещённые веса:", padding_weights)
print("Неправильная маска нулём:", softmax_rows([[1/np.sqrt(2), 0]]))
try:
    attention(X, X, X, np.zeros((3, 3), dtype=bool))
except ValueError as e:
    print("Ожидаемая ошибка:", e)
else:
    raise AssertionError("Полностью закрытая строка должна быть отклонена")''',
'''assert padding_weights.shape == (3, 3)
assert np.allclose(padding_weights.sum(axis=1), 1)
assert softmax_rows([[1, 0]])[0, 1] > 0''',
'Последний запрос в этом демонстрационном массиве вычисляется, но последний ключ запрещён. Это не полноценный пакетный трансформер: маска потерь и удаление выходов padding-запросов потребовали бы отдельного решения.'),
task('5. Перестановка и позиционный сигнал — 15 минут',
'''Без масок и позиций сравните attention(X, X, X) с attention на переставленных строках. Результат должен переставиться так же. Затем добавьте Pos к исходному X и к переставленному X, сохраняя Pos по местам. Сохраните выходы как `with_position` и `permuted_with_position`, а максимальную абсолютную разницу `np.max(np.abs(permuted_with_position - with_position[permutation]))` — в `position_difference`. Покажите, что простая перестановка прежнего выхода уже не обязана совпадать. Позиции заданы вручную, модель не обучалась.''',
'''permutation = np.array([2, 0, 1])
Pos = np.array([[0., 0.], [0.5, 0.], [0., 0.5]])
# TODO: сравнение без позиций; with_position, permuted_with_position, position_difference.
raise NotImplementedError''',
'''permutation = np.array([2, 0, 1])
Pos = np.array([[0., 0.], [0.5, 0.], [0., 0.5]])
base, _ = attention(X, X, X)
permuted, _ = attention(X[permutation], X[permutation], X[permutation])
print("Ошибка перестановочного равенства без позиций:", np.max(np.abs(permuted - base[permutation])))
assert np.allclose(permuted, base[permutation])
XP = X + Pos
XP_permuted = X[permutation] + Pos
with_position, _ = attention(XP, XP, XP)
permuted_with_position, _ = attention(XP_permuted, XP_permuted, XP_permuted)
position_difference = np.max(np.abs(permuted_with_position - with_position[permutation]))
print("Разница с позиционным сигналом:", position_difference)
assert not np.allclose(permuted_with_position, with_position[permutation])''',
'''assert position_difference > 1e-6''',
'При перестановке слов позиционные векторы остаются привязаны к местам. Если переставить X+Pos целиком, снова получится простая эквивариантность: это был бы другой эксперимент.'),
code('''# Мини-пример объединения голов, не полноценное обучение multi-head.
head1 = np.array([[1., 2.]])
head2 = np.array([[10., 20.]])
print("Конкатенация:", np.concatenate([head1, head2], axis=1))
for length in [1024, 4096]:
    print("N:", length, "Одна матрица float32, MiB:", length*length*4/(2**20))
same_values = np.array([[1., 2.], [1., 2.]])
print("Разные веса, одинаковый выход:", np.array([0.9,0.1])@same_values,
      np.array([0.2,0.8])@same_values)'''),
md('''## 6. Выводы и защита — 15 минут

Первые 10 минут — разбор объединения голов, памяти и одинаковых V. Последние 5 минут — итоговые выводы. Перечислите проверенные свойства, объясните одно нарушение и его исправление. Не интерпретируйте вручную заданные веса как понимание русского языка.

**Мои выводы:** TODO.''', teacher='''## Эталон интерпретации

Проверенный softmax для строки (1000,1001,1002) дал (0,090031;0,244728;0,665241). Добавление 10000 ко всем оценкам не изменило распределение с точностью вычислений; обе строки матрицы нормируются независимо.

В ручном примере веса без маски равны [[0,66976155;0,33023845],[0,33023845;0,66976155]], выходы — (6,69761549;6,60476901) и (3,30238451;13,39523099). С causal-маской первая строка весов становится (1;0), первый выход (10;0), второй выход сохраняется. Это совпадает с лекцией.

В трёхпозиционном опыте изменение будущего V[2] на (100;−50) не изменило первые два causal-выхода: максимальная разница 0. Без маски максимальное изменение ранних выходов≈40,111209. Так подтверждён именно запрет передачи информации, а не только форма нарисованного треугольника.

Совмещённая causal/padding-маска дала веса [[1;0;0],[0,33023845;0,66976155;0],[0,5;0,5;0]]. Последний столбец нулевой. Полностью закрытая строка вызвала ValueError. Ошибочная подстановка 0 вместо −inf оставила вес запрещённого ключа≈0,33023845, то есть доступ не был запрещён.

Без позиций максимальное расхождение перестановочного равенства равно 0. С позиционными добавками, закреплёнными за местами, разница≈0,349083. Это показывает наличие используемого числового сигнала о позиции в заданном примере, а не обучение русскому синтаксису.

Конкатенация двух выходов дала (1;2;10;20), а не среднее (5,5;11). Одна полная матрица float32 занимает 4 MiB при N=1024 и 64 MiB при N=4096; это не память всей модели. Два разных набора весов при V₁=V₂=(1;2) дали одинаковый выход (1;2), поэтому одна тепловая карта не исчерпывает объяснение.

Ответы защиты: ось ключей нормирует альтернативы одного запроса; деление на √d_k не нормирует индивидуальные длины Q/K как косинус; exp(0)>0; диагональ разрешена, потому что текущий вход предсказывает следующий токен; маска ключей ограничивает источники информации, маска потерь — оцениваемые цели. Одинаковые V могут давать один выход при разных нормированных весах.'''),
]}
