"""Read-only L02 fact review; writes only this review's JSON evidence."""
import ast
import hashlib
import inspect
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding="utf-8")
files = [
    "source/lectures/L02.md", "source/labs/L02.py", "source/labs/L02.json",
    "dist/teacher/L02/solution.ipynb", "data/requests.csv",
    "dist/teacher/data/requests.csv", "scripts/build_notebooks.py",
]
evidence = {
    "review_date": "2026-09-08",
    "versions": {"python": sys.version, "sklearn": sklearn.__version__},
    "sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files},
}
nb = json.loads((ROOT / "dist/teacher/L02/solution.ipynb").read_text(encoding="utf-8"))
cells = nb["cells"]
code = ["".join(c["source"]) for c in cells if c["cell_type"] == "code"]
outputs = []
for i, c in enumerate(cells):
    if c["cell_type"] != "code":
        continue
    plain = []
    for o in c.get("outputs", []):
        assert o.get("output_type") != "error", (i, o)
        if "text" in o:
            plain.append("".join(o["text"]))
        if "text/plain" in o.get("data", {}):
            plain.append("".join(o["data"]["text/plain"]))
    outputs.append({"cell_index_zero_based": i, "execution_count": c.get("execution_count"), "outputs": plain})
assert [x["execution_count"] for x in outputs] == list(range(1, 14))
evidence["notebook_outputs"] = outputs
syntax = ast.parse((ROOT / "source/labs/L02.py").read_text(encoding="utf-8"))
solutions = [ast.literal_eval(n.args[3]) for n in ast.walk(syntax)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "task"]
assert len(solutions) == 5
assert all(s.strip() in [c.strip() for c in code] for s in solutions)
prose = json.loads((ROOT / "source/labs/L02.json").read_text(encoding="utf-8"))
assert prose["teacher_ending"] in ["".join(c["source"]) for c in cells if c["cell_type"] == "markdown"]
evidence["source_sync"] = {"five_solution_cells_match_python": True, "teacher_ending_matches_json": True}
assert evidence["sha256"]["data/requests.csv"] == evidence["sha256"]["dist/teacher/data/requests.csv"]
df = pd.read_csv(ROOT / "data/requests.csv", keep_default_na=False)
parts = {s: df[df["split"].eq(s)] for s in ["train", "validation", "test"]}
groups = {s: set(p["group_id"]) for s, p in parts.items()}
assert all(groups[a].isdisjoint(groups[b]) for a, b in [("train", "validation"), ("train", "test"), ("validation", "test")])
assert df.groupby("group_id").size().eq(5).all()
assert df.groupby("group_id")["label"].nunique().eq(1).all()
evidence["data"] = {"rows": len(df), "groups": int(df["group_id"].nunique()), "rows_per_group": 5,
    "splits": {s: {"rows": len(p), "groups": len(groups[s]), "class_counts": p["label"].value_counts().to_dict()} for s, p in parts.items()},
    "group_intersections_empty": True}

toy = ["книга книга библиотека", "книга продление", "общежитие оплата"]
vectorizer = TfidfVectorizer(smooth_idf=True, norm="l2", sublinear_tf=False)
matrix = vectorizer.fit_transform(toy)
idf_book = 1 + math.log(4 / 3)
idf_other = 1 + math.log(2)
length = math.hypot(idf_other, 2 * idf_book)
assert np.allclose(matrix.toarray()[0], [idf_other / length, 2 * idf_book / length, 0, 0, 0])
scores = np.array([2 * .8 - .1, -.8 + 2 * .1])
probabilities = np.exp(scores - scores.max()) / np.exp(scores - scores.max()).sum()
updated_scores = scores + [.08, 0]
updated_probabilities = np.exp(updated_scores - updated_scores.max()) / np.exp(updated_scores - updated_scores.max()).sum()
assert np.allclose(scores, [1.5, -.6])
assert -math.log(updated_probabilities[0]) < -math.log(probabilities[0])
evidence["manual"] = {
    "toy": {"vocabulary": vectorizer.get_feature_names_out().tolist(), "idf": vectorizer.idf_.tolist(),
            "unnormalized_first": [idf_other, 2 * idf_book, 0, 0, 0], "first_l2_length_before_normalization": length,
            "normalized_matrix": matrix.toarray().tolist()},
    "linear": {"features": [.8, .1], "scores": scores.tolist(), "softmax": probabilities.tolist(),
               "loss_library": -math.log(probabilities[0]), "loss_p09": -math.log(.9), "loss_p01": -math.log(.1),
               "updated_weight": 2.1, "updated_scores": updated_scores.tolist(),
               "updated_softmax": updated_probabilities.tolist(), "updated_loss_library": -math.log(updated_probabilities[0]),
               "gradient_library_book_single_example_no_regularization": float((probabilities[0] - 1) * .8)},
    "always_A_90_10": {"confusion_true_rows": [[90, 0], [10, 0]], "accuracy": .9,
                       "precision_A": .9, "recall_A": 1, "F1_A": 180 / 190, "F1_B": 0, "macro_F1": 90 / 190},
    "six_balanced_always_one": {"accuracy": 1 / 6, "F1_predicted_class": 2 / 7, "macro_F1": 1 / 21},
}

# The stored notebook has only one representative per erroneous group. One small
# char_wb fit independently verifies all 25 variants and punctuation controls.
started = time.perf_counter()
selected = Pipeline([
    ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), max_features=5000)),
    ("clf", LogisticRegression(C=1, max_iter=1000, random_state=42)),
])
selected.fit(parts["train"]["text"], parts["train"]["label"])
pred_test = selected.predict(parts["test"]["text"])
pred_valid = selected.predict(parts["validation"]["text"])
labels = sorted(df["label"].unique())
metric = lambda p, y: {"accuracy": accuracy_score(p["label"], y), "macro_f1": f1_score(p["label"], y, labels=labels, average="macro", zero_division=0)}
test_scores = metric(parts["test"], pred_test)
assert math.isclose(test_scores["accuracy"], .7916666666666666, abs_tol=1e-14)
assert math.isclose(test_scores["macro_f1"], .7651970897407003, abs_tol=1e-14)
errors = parts["test"].assign(predicted=pred_test).loc[lambda x: x["label"].ne(x["predicted"])]
assert len(errors) == 25
controls = ["", "жжжжжжжжж", "Не открывается виртуальная комната конференции",
    "Мне нужна помощь в подборе источников для курсовой.",
    "Мне нужна помощь в подборе источников для курсовой",
    "Здравствуйте! Мне нужна помощь в подборе источников для курсовой."]
control_pred = selected.predict(controls)
control_nnz = selected["tfidf"].transform(controls).getnnz(axis=1).tolist()
assert control_pred.tolist() == ["it", "it", "it", "it", "study", "study"]
assert control_nnz[:3] == [0, 0, 64]
evidence["char_wb_verification"] = {
    "fit_seconds": time.perf_counter() - started,
    "validation_scores": metric(parts["validation"], pred_valid), "test_scores": test_scores,
    "labels": labels, "confusion_matrix_true_rows": confusion_matrix(parts["test"]["label"], pred_test, labels=labels).tolist(),
    "errors": errors.to_dict("records"),
    "error_groups": {g: p["predicted"].value_counts().to_dict() for g, p in errors.groupby("group_id")},
    "controls": [{"text": t, "predicted": p, "nnz": n} for t, p, n in zip(controls, control_pred, control_nnz)],
    "intercepts": dict(zip(selected["clf"].classes_, selected["clf"].intercept_.tolist())),
    "implementation_char_wb": inspect.getsource(CountVectorizer._char_wb_ngrams),
}
assert evidence["char_wb_verification"]["error_groups"]["library-20"] == {"study": 4, "it": 1}
evidence["result"] = "all numerical and exact-input checks passed; see facts_review.md for wording observations"
(OUT / "facts_evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"result": evidence["result"], "char_fit_seconds": evidence["char_wb_verification"]["fit_seconds"],
                  "manual": evidence["manual"], "char_metrics": test_scores,
                  "errors_by_group": evidence["char_wb_verification"]["error_groups"]}, ensure_ascii=False, indent=2))
