import json
import os

import joblib
import numpy as np
import optuna
import torch
import torch.nn as nn
from sklearn.decomposition import PCA
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.random_projection import SparseRandomProjection

import onnx
from onnx import helper
from onnx import numpy_helper

from ...utils.logging import logger
from ... import ONNX_TARGET_OPSET, ONNX_IR_VERSION


MAX_NUM_TRIALS = 10
MIN_FEATURES = 4
MAX_FEATURES = 512


def find_params(X, y, num_trials):
    """
    Optimize the number of latent components and regularization parameter for binary classification
    using Principal Component Analysis (PCA) and Stochastic Gradient Descent Classifier (SGDClassifier).

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        The input data matrix.
    y : array-like of shape (n_samples,)
        The target binary labels.

    Returns
    -------
    results : dict
        A dictionary containing the optimal number of latent components:
        - "n_components": int, the optimal number of components.

    Notes
    -----
    - The function uses PCA to reduce dimensionality and Optuna for hyperparameter optimization.
    - The optimization process includes pruning of unpromising trials using a MedianPruner.
    - The ROC-AUC score is used as the evaluation metric for model performance.
    - The function performs stratified shuffle split cross-validation to ensure balanced class distribution
      in training and testing sets.
    """
    do_latent = True
    if not do_latent:
        logger.info("Skipping latent variable generation.")
        return {"n_components": None}
    logger.info("Finding optimal latent variable parameters...")

    cv = StratifiedShuffleSplit(n_splits=3, test_size=0.2, random_state=42)

    min_n_components = []
    max_n_components = []
    seed_n_components = []

    logger.debug("Preparing folds for cross-validation...")
    folds = []
    for train_index, test_index in cv.split(X, y):
        logger.debug("Precomputing reductions for a fold...")
        X_tr, X_te = X[train_index], X[test_index]
        y_tr, y_te = y[train_index], y[test_index]
        logger.debug(f"Train shape: {X_tr.shape}, Test shape: {X_te.shape}")
        n_components = min(X_tr.shape[1], X_tr.shape[0]) - 1
        n_components = min(n_components, MAX_FEATURES)
        logger.debug(f"Using n_components={n_components} for PCA.")
        reducer = PCA(
            n_components=n_components, svd_solver="randomized", random_state=42
        )
        reducer.fit(X_tr)
        X_tr = reducer.transform(X_tr)
        X_te = reducer.transform(X_te)
        folds += [(X_tr, X_te, y_tr, y_te)]
        explained_variance_ratio_cumsum = np.cumsum(reducer.explained_variance_ratio_)
        n_components_80 = np.searchsorted(explained_variance_ratio_cumsum, 0.8) + 1
        n_components_90 = np.searchsorted(explained_variance_ratio_cumsum, 0.9) + 1
        n_components_99 = np.searchsorted(explained_variance_ratio_cumsum, 0.9) + 1
        min_n_components += [n_components_80]
        seed_n_components += [n_components_90]
        max_n_components += [n_components_99]

    min_n_components = int(np.mean(min_n_components))
    seed_n_components = int(np.mean(seed_n_components))
    max_n_components = int(np.mean(max_n_components))

    def objective(trial):
        n_components = trial.suggest_int(
            "n_components", min_n_components, max_n_components, step=1
        )
        alpha = trial.suggest_float("alpha", 1e-6, 1e-2, log=True)

        clf = SGDClassifier(
            loss="log_loss",
            alpha=alpha,
            class_weight="balanced",
            max_iter=2000,
            tol=1e-3,
            early_stopping=True,
            validation_fraction=0.2,
            n_iter_no_change=5,
            random_state=42,
        )
        scores = []
        for fold_idx, (X_tr, X_te, y_tr, y_te) in enumerate(folds):
            X_tr = X_tr[:, :n_components]
            X_te = X_te[:, :n_components]
            clf.fit(X_tr, y_tr)
            proba = clf.predict_proba(X_te)[:, 1]
            score = roc_auc_score(y_te, proba)
            scores += [score]
            trial.report(np.mean(scores), step=fold_idx)
            if trial.should_prune():
                raise optuna.TrialPruned()
        return float(np.mean(scores))

    pruner = optuna.pruners.MedianPruner(n_warmup_steps=5)
    study = optuna.create_study(direction="maximize", pruner=pruner)
    initial_params = {
        "n_components": seed_n_components,
        "alpha": 1e-4,
    }
    study.enqueue_trial(params=initial_params)
    study.optimize(
        objective, n_trials=min(num_trials, MAX_NUM_TRIALS), show_progress_bar=True
    )
    logger.info("Best trial:")
    logger.info(f"  ROC-AUC: {study.best_value}")
    logger.info(f"  Params: {study.best_params}")

    results = {"n_components": min(MAX_FEATURES, study.best_params["n_components"])}

    return results


class LatentVariables(object):
    """
    A class for reducing the dimensionality of data for binary classification tasks
    using Principal Component Analysis (PCA).

    Parameters
    ----------
    n_components : int
        The number of principal components to retain during dimensionality reduction.

    Methods
    -------
    fit(X, y=None)
        Fits a reducer to the input data.
    transform(X, y=None)
        Transforms the input data using the fitted reducer.
    save(model_dir: str)
        Saves the reducer and its metadata to the specified directory.
    load(model_dir: str)
        Loads the reducer and its metadata from the specified directory.
    """

    def __init__(self, n_components: int = None):
        """
        Initializes the class with the specified number of components.
        Parameters
        ----------
        n_components : int
            The number of components to use for the binary classification model.
        """
        self.n_components = n_components

    def fit(self, X, y=None):
        """
        Fit the latent variable reducer using the provided data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The input data to fit the latent variable reducer.
        y : array-like of shape (n_samples,), optional
            The target values (ignored in this method, included for compatibility).

        Returns
        -------
        self : object
            Returns the instance of the latent variable reducer.
        """
        self.input_dim = X.shape[1]
        if self.n_components is None:
            self.reducer = None
            return self
        logger.info(
            "Fitting latent reducer with {0} components...".format(self.n_components)
        )
        n_components = min(self.n_components, X.shape[1])
        self.reducer = SparseRandomProjection(
            n_components=n_components, random_state=42
        )
        self.reducer.fit(X)
        return self

    def transform(self, X, y=None):
        """
        Transform the input data using the fitted dimensionality reducer.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The input data to transform.
        y : None, optional
            Ignored. This parameter exists for compatibility with scikit-learn
            transformers.

        Returns
        -------
        X : array-like of shape (n_samples, n_components)
            The transformed data.

        Raises
        ------
        RuntimeError
            If the reducer has not been fitted prior to calling this method.
        """
        if not hasattr(self, "reducer"):
            raise RuntimeError(
                "The reducer has not been fitted yet. Please call 'fit' before 'transform'."
            )
        if self.reducer is None:
            return X
        logger.info("Transforming latent reducer using PCA...")
        X = self.reducer.transform(X)
        return X

    def save(self, name: str, model_dir: str):
        """
        Save the latent variable reducer to the specified directory.

        This method saves the metadata and the reducer object to the given directory.
        If the directory does not exist, it will be created.

        Parameters
        ----------
        model_dir : str
            The directory where the latent variable reducer and its metadata will be saved.


        Notes
        -----
        - The metadata is saved as a JSON file named `latent_reducer_metadata.json`.
        - The reducer object is serialized and saved as a joblib file named `latent_reducer.joblib`.
        """
        if not os.path.exists(model_dir):
            logger.info(
                f"Creating directory {model_dir} for saving the latent reducer."
            )
            os.makedirs(model_dir)
        metadata = {"n_components": self.n_components, "input_dim": self.input_dim}
        meta_path = os.path.join(model_dir, f"{name}_metadata.json")
        with open(meta_path, "w") as f:
            json.dump(metadata, f)
        reducer_path = os.path.join(model_dir, f"{name}.joblib")
        joblib.dump(self.reducer, reducer_path)

    @classmethod
    def load(cls, name: str, model_dir: str):
        """
        Load a latent variable reducer object from a specified directory.

        Parameters
        ----------
        model_dir : str
            The directory where the latent variable reducer model and metadata are stored.

        Returns
        -------
        cls
            An instance of the class with the loaded reducer and metadata.

        Raises
        ------
        FileNotFoundError
            If the specified directory does not exist.
            If the metadata file "latent_reducer_metadata.json" is not found in the directory.
            If the reducer file "latent_reducer.joblib" is not found in the directory.

        Notes
        -----
        The method expects the directory to contain two files:
        1. "latent_reducer_metadata.json" - A JSON file containing metadata such as the number of components.
        2. "latent_reducer.joblib" - A serialized file containing the reducer object.
        """
        if not os.path.exists(model_dir):
            raise FileNotFoundError(f"The directory {model_dir} does not exist.")
        meta_path = os.path.join(model_dir, f"{name}_metadata.json")
        if not os.path.exists(meta_path):
            raise FileNotFoundError(
                f"The metadata file {meta_path} does not exist in the directory {model_dir}."
            )
        with open(meta_path, "r") as f:
            metadata = json.load(f)
        obj = cls(n_components=metadata["n_components"])
        obj.input_dim = metadata["input_dim"]
        reducer_path = os.path.join(model_dir, f"{name}.joblib")
        if not os.path.exists(reducer_path):
            raise FileNotFoundError(
                f"The reducer file {reducer_path} does not exist in the directory {model_dir}."
            )
        obj.reducer = joblib.load(reducer_path)
        return obj


class DenseProjectionLayer(nn.Module):
    """Dense wrapper for sklearn SparseRandomProjection so ONNX export succeeds."""

    def __init__(self, components):
        super().__init__()
        n_components, n_features = components.shape
        self.encoder = nn.Linear(n_features, n_components, bias=False)
        self.encoder.weight.data = torch.tensor(components, dtype=torch.float32)
        for p in self.parameters():
            p.requires_grad = False

    def forward(self, x):
        return self.encoder(x)


def convert_to_onnx(name: str, model_dir: str):
    """
    Converts a latent variable reducer for binary classification into an ONNX model
    with sparse storage. The function first exports a dense ONNX model and then patches
    it to replace the dense weight matrix with a sparse initializer.

        Path to the directory containing the latent variable reducer model
        (`latent_reducer.joblib`).

    Returns
    -------
    str
        The file path to the generated sparse ONNX model.

    Raises
    ------
    RuntimeError
        If the latent reducer is not found in the specified directory, or if the
        projection matrix initializer cannot be located in the ONNX export.

    Notes
    -----
    - The function assumes that the latent reducer is stored as a `LatentVariablesForBinaryClassification`
      object and that its `reducer` attribute contains a trained projection matrix.
    - The ONNX model is first exported in dense format using PyTorch's `torch.onnx.export`
      and then modified to use sparse storage by replacing the dense initializer with a
      sparse tensor.
    - The intermediate dense ONNX file is removed after the sparse ONNX model is created.
    """
    latent_reducer = LatentVariables.load(name, model_dir)
    if latent_reducer.reducer is None:
        logger.info("No latent reducer found, skipping ONNX conversion.")
        return None
    reducer = latent_reducer.reducer
    input_dim = latent_reducer.input_dim
    opset_version = ONNX_TARGET_OPSET

    logger.info("Converting latent reducer to ONNX with sparse storage")

    components = reducer.components_.toarray()
    model = DenseProjectionLayer(components)
    dummy_input = torch.randn(1, input_dim, dtype=torch.float32)

    dense_path = os.path.join(model_dir, f"{name}_dense.onnx")
    torch.onnx.export(
        model,
        dummy_input,
        dense_path,
        input_names=[f"input_{name}"],
        output_names=[f"output_{name}"],
        dynamic_axes={
            f"input_{name}": {0: "batch_size"},
            f"output_{name}": {0: "batch_size"},
        },
        opset_version=opset_version,
    )

    model_onnx = onnx.load(dense_path)

    dense_init = None
    dense_array = None
    for init in model_onnx.graph.initializer:
        arr = numpy_helper.to_array(init)
        if arr.ndim == 2:
            dense_init = init
            dense_array = arr
            break
    if dense_init is None:
        raise RuntimeError(
            "Could not find 2D projection matrix initializer in ONNX export"
        )

    nz_rows, nz_cols = np.nonzero(dense_array)
    values = dense_array[nz_rows, nz_cols].astype(np.float32)
    indices = np.stack([nz_rows, nz_cols], axis=1).astype(np.int64)

    values_proto = numpy_helper.from_array(values)
    indices_proto = numpy_helper.from_array(indices)

    sparse_init = helper.make_sparse_tensor(
        values=values_proto,
        indices=indices_proto,
        dims=dense_array.shape,
    )

    sparse_init.values.name = dense_init.name

    model_onnx.graph.sparse_initializer.append(sparse_init)
    model_onnx.graph.initializer.remove(dense_init)

    model_onnx.ir_version = ONNX_IR_VERSION
    model_onnx.graph.name = f"{name}"
    for node in model_onnx.graph.node:
        if node.name:
            node.name = f"{node.name}_{name}"

    onnx_path = os.path.join(model_dir, f"{name}.onnx")
    onnx.checker.check_model(model_onnx)
    onnx.save(model_onnx, onnx_path)

    os.remove(dense_path)

    return onnx_path
