import json
import joblib
import os
import numpy as np
import optuna
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.base import BaseEstimator, ClassifierMixin

import onnx
from onnx import helper, numpy_helper, TensorProto

from ... import ONNX_TARGET_OPSET, ONNX_IR_VERSION
from ...utils.logging import logger

MAX_NUM_TRIALS = 100
MIN_NUM_TRIALS = 10
MAX_ITER = 1000
SPARSITY_THRESHOLD = 0.9


def _is_sparse(X):
    if hasattr(X, "toarray"):
        zero_fraction = 1.0 - (X.count_nonzero() / np.prod(X.shape))
    else:
        zero_fraction = np.mean(X == 0)
    return zero_fraction >= SPARSITY_THRESHOLD


def use_full(X):
    if X.shape[1] <= 512:
        return True
    else:
        return _is_sparse(X)


def find_params(X, y, num_trials):
    """
    Tune either alpha (= 1/C) for SGDClassifier or C for LogisticRegression
    using out-of-fold ROC-AUC.
    Returns {"alpha": best_alpha, "use_logreg": bool}.
    """
    num_trials = min(num_trials, MAX_NUM_TRIALS)
    X = np.asarray(X)
    y = np.asarray(y)

    do_full = use_full(X)
    n_splits = 5
    random_state = 42
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    if do_full:
        logger.info(
            f"Running Optuna for LogisticRegression with {num_trials} trials..."
        )

        def objective(trial):
            C = trial.suggest_float("C", 1e-4, 1e2, log=True)
            oof = np.full(len(y), np.nan, dtype=np.float32)
            for tr, va in cv.split(X, y):
                clf = LogisticRegression(
                    C=C,
                    class_weight="balanced",
                    solver="saga",
                    max_iter=MAX_ITER,
                    n_jobs=-1,
                    random_state=random_state,
                )
                clf.fit(X[tr], y[tr])
                oof[va] = clf.predict_proba(X[va])[:, 1].astype(np.float32)
            if np.isnan(oof).any():
                return 0.5
            return roc_auc_score(y, oof)

        study = optuna.create_study(
            direction="maximize", pruner=optuna.pruners.MedianPruner()
        )
        study.enqueue_trial({"C": 1.0})
        study.optimize(objective, n_trials=num_trials, n_jobs=-1)

        best_C = float(study.best_params["C"])
        logger.info(f"Best LogisticRegression C: {best_C}")
        return {"C": best_C, "use_logreg": True}

    else:
        num_trials = max(MIN_NUM_TRIALS, num_trials)

        logger.info(
            f"Running Optuna with {num_trials} trials for SGD logistic regression head..."
        )

        def objective(trial):
            C = trial.suggest_float("C", 1e-4, 1e2, log=True)
            alpha = 1.0 / C

            oof = np.full(len(y), np.nan, dtype=np.float32)
            for tr, va in cv.split(X, y):
                clf = SGDClassifier(
                    loss="log_loss",
                    alpha=alpha,
                    class_weight="balanced",
                    max_iter=MAX_ITER,
                    tol=1e-3,
                    n_jobs=-1,
                    random_state=random_state,
                )
                clf.fit(X[tr], y[tr])
                oof[va] = clf.predict_proba(X[va])[:, 1].astype(np.float32)

            if np.isnan(oof).any():
                return 0.5
            return roc_auc_score(y, oof)

        study = optuna.create_study(
            direction="maximize", pruner=optuna.pruners.MedianPruner()
        )
        study.enqueue_trial({"C": 1.0})
        study.optimize(objective, n_trials=num_trials, n_jobs=-1)

        best_C = float(study.best_params["C"])
        best_alpha = 1.0 / best_C
        logger.info(f"Best C: {best_C} (alpha={best_alpha})")
        return {"alpha": best_alpha, "use_logreg": False}


class Head(BaseEstimator, ClassifierMixin):
    def __init__(self, alpha=None, C=None, use_logreg=False):
        self.alpha = alpha
        self.C = C
        self.use_logreg = use_logreg

    def fit(self, X, y):
        X = np.asarray(X)
        self.use_logreg = self.use_logreg

        if self.use_logreg:
            logger.info("Fitting LogisticRegression head...")
            self.model = LogisticRegression(
                C=self.C or 1.0,
                class_weight="balanced",
                solver="saga",
                max_iter=MAX_ITER,
                n_jobs=-1,
                random_state=42,
            )
            self.model.fit(X, y)
            self.calibrate(X, y)
        else:
            logger.info("Fitting SGD logistic regression head...")
            self.model = SGDClassifier(
                loss="log_loss",
                alpha=self.alpha,
                class_weight="balanced",
                max_iter=MAX_ITER,
                tol=1e-3,
                n_jobs=-1,
                random_state=42,
            )
            self.model.fit(X, y)
            self.calibrate(X, y)

        self.input_dim = X.shape[1]
        return self

    def calibrate(self, X, y):
        logger.info("Calibrating probabilities with logistic regression...")
        y_hat = self.model.predict_proba(X)[:, 1]
        self.calibrator = LogisticRegression(class_weight="balanced", solver="lbfgs")
        self.calibrator.fit(y_hat.reshape(-1, 1), y)
        self.score = roc_auc_score(y, y_hat)
        logger.info(f"ROC-AUC: {self.score:.4f}")
        return self.score

    def predict_proba(self, X):
        y_hat = self.model.predict_proba(X)[:, 1]
        y_hat = self.calibrator.predict_proba(y_hat.reshape(-1, 1))[:, 1]
        return np.vstack([1 - y_hat, y_hat]).T

    def predict(self, X):
        y_hat = self.model.predict_proba(X)[:, 1]
        return (y_hat > 0.5).astype(int)

    def save(self, name: str, model_dir: str):
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        metadata = {
            "alpha": self.alpha,
            "C": self.C,
            "score": self.score,
            "input_dim": self.input_dim,
            "use_logreg": bool(self.use_logreg),
        }
        with open(os.path.join(model_dir, f"{name}_metadata.json"), "w") as f:
            json.dump(metadata, f)
        joblib.dump(self.model, os.path.join(model_dir, f"{name}_model.joblib"))
        joblib.dump(
            self.calibrator, os.path.join(model_dir, f"{name}_calibrator.joblib")
        )

    @classmethod
    def load(cls, name: str, model_dir: str):
        with open(os.path.join(model_dir, f"{name}_metadata.json"), "r") as f:
            metadata = json.load(f)
        model = joblib.load(os.path.join(model_dir, f"{name}_model.joblib"))
        head = cls(
            alpha=metadata.get("alpha"),
            C=metadata.get("C"),
            use_logreg=bool(metadata.get("use_logreg", False)),
        )
        head.model = model
        head.score = metadata["score"]
        head.input_dim = metadata["input_dim"]
        head.calibrator = joblib.load(
            os.path.join(model_dir, f"{name}_calibrator.joblib")
        )
        return head


def convert_to_onnx(name: str, model_dir: str) -> str:
    """
    Convert the head model into ONNX:
      - For SGD + calibrator: p = sigmoid( a * (w^T x + b) + c )
      - For LogisticRegression: p = sigmoid(w^T x + b)
    """
    head = Head.load(name, model_dir)
    base = head.model
    input_dim = int(head.input_dim)

    if head.use_logreg:
        w = np.asarray(base.coef_, dtype=np.float32).reshape(1, input_dim)
        b = np.asarray(base.intercept_, dtype=np.float32).reshape(
            1,
        )
        a = np.array([1.0], dtype=np.float32)
        c = np.array([0.0], dtype=np.float32)
    else:
        cal = head.calibrator
        w = np.asarray(base.coef_, dtype=np.float32).reshape(1, input_dim)
        b = np.asarray(base.intercept_, dtype=np.float32).reshape(
            1,
        )
        a = float(np.asarray(cal.coef_, dtype=np.float32).reshape(1, 1)[0, 0])
        c = float(
            np.asarray(cal.intercept_, dtype=np.float32).reshape(
                1,
            )[0]
        )

    W_init = numpy_helper.from_array(w.T.astype(np.float32), name=f"{name}_W")
    b_init = numpy_helper.from_array(b.astype(np.float32), name=f"{name}_b")
    a_init = numpy_helper.from_array(np.array([a], dtype=np.float32), name=f"{name}_a")
    c_init = numpy_helper.from_array(np.array([c], dtype=np.float32), name=f"{name}_c")
    shape_init = numpy_helper.from_array(
        np.array([-1], dtype=np.int64), name=f"{name}_shape1d"
    )

    X = helper.make_tensor_value_info(
        f"input_{name}", TensorProto.FLOAT, ["batch_size", input_dim]
    )
    Y = helper.make_tensor_value_info(
        f"output_{name}", TensorProto.FLOAT, ["batch_size"]
    )

    gemm = helper.make_node(
        "Gemm",
        [f"input_{name}", f"{name}_W", f"{name}_b"],
        [f"{name}_z1"],
        name=f"{name}_Gemm",
    )
    sig1 = helper.make_node(
        "Sigmoid", [f"{name}_z1"], [f"{name}_p1"], name=f"{name}_Sigmoid1"
    )
    mul = helper.make_node(
        "Mul", [f"{name}_p1", f"{name}_a"], [f"{name}_s1"], name=f"{name}_Mul"
    )
    add = helper.make_node(
        "Add", [f"{name}_s1", f"{name}_c"], [f"{name}_z2"], name=f"{name}_Add"
    )
    sig2 = helper.make_node(
        "Sigmoid", [f"{name}_z2"], [f"{name}_p2"], name=f"{name}_Sigmoid2"
    )
    reshape = helper.make_node(
        "Reshape",
        [f"{name}_p2", f"{name}_shape1d"],
        [f"output_{name}"],
        name=f"{name}_Reshape1D",
    )

    graph = helper.make_graph(
        nodes=[gemm, sig1, mul, add, sig2, reshape],
        name=f"{name}",
        inputs=[X],
        outputs=[Y],
        initializer=[W_init, b_init, a_init, c_init, shape_init],
    )

    model = helper.make_model(
        graph,
        producer_name=f"{name}",
        opset_imports=[helper.make_operatorsetid("", ONNX_TARGET_OPSET)],
    )
    model.ir_version = ONNX_IR_VERSION
    onnx.checker.check_model(model)

    onnx_path = os.path.join(model_dir, f"{name}.onnx")
    onnx.save(model, onnx_path)
    return onnx_path
