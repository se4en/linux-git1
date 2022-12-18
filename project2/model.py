from typing import Any, Dict, List, Tuple
import json
import os

from omegaconf import DictConfig, OmegaConf
import hydra
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import (
    StratifiedKFold,
    KFold,
    cross_val_predict,
)
from sklearn.metrics import (
    roc_auc_score,
    f1_score,
    precision_score,
    recall_score,
    roc_curve,
)
from catboost import CatBoostClassifier


def preprocess_data(
    path_to_data: str, features: List[str], target_id: int, retro: bool
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(path_to_data)

    if retro:
        df = df[df.index < 100]
    else:
        df = df[df.index >= 100]

    df.dropna(inplace=True)

    df = df[df["f_6"] != 9]
    df = df[df["f_4"] != 2]
    df = df[df["f_5"] != 9]
    df = df[df["f_7"] != 0]

    df = df.astype(int)

    assert target_id in {1, 2, 3}, "Wrong target id"
    target_name = f"target_{target_id}"
    y = df.pop(target_name)
    X = df[features]

    return X, y


def train_model(
    X: pd.DataFrame,
    y: pd.Series,
    seed: int,
    kfolds: int,
    stratified: bool,
    shuffle: bool,
) -> np.ndarray:
    if stratified:
        cv = StratifiedKFold(kfolds, random_state=seed, shuffle=shuffle)
    else:
        cv = KFold(kfolds, random_state=seed, shuffle=shuffle)

    model = CatBoostClassifier(
        task_type="CPU",
        random_state=seed,
        verbose=False,
        cat_features=list(X.columns),
    )

    y_pred = cross_val_predict(model, X, y, cv=cv, method="predict_proba")
    return y_pred[:, 1]


def save_results(
    y_pred: np.ndarray,
    y: pd.Series,
    th: float,
    metrics_path: str,
    plot_path: str,
    seed: int,
) -> None:
    y_pred_vals = y_pred > th

    os.remove(metrics_path)
    with open(metrics_path, "w") as f:
        json.dump(
            {
                "recall": recall_score(y, y_pred_vals),
                "precision": precision_score(y, y_pred_vals),
                "f1": f1_score(y, y_pred_vals),
                "seed": seed,
            },
            f,
        )

    plt.figure(figsize=(10, 10))
    lw = 2
    fpr, tpr, _ = roc_curve(y, y_pred)
    plt.plot(
        fpr,
        tpr,
        color="darkorange",
        lw=lw,
        label="ROC кривая (площадь: %0.3f)" % roc_auc_score(y, y_pred),
    )
    plt.plot([0, 1], [0, 1], color="navy", lw=lw, linestyle="--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False positive rate", fontsize=16)
    plt.ylabel("True positive rate", fontsize=16)
    plt.legend(loc="lower right")
    os.remove(plot_path)
    plt.savefig(plot_path, dpi=300)


@hydra.main(version_base=None, config_path=".", config_name="config")
def main(cfg: DictConfig) -> None:
    X, y = preprocess_data(
        cfg.data.path, cfg.data.features, cfg.data.target, cfg.data.retro
    )
    preds = train_model(
        X, y, cfg.train.seed, cfg.train.kfolds, cfg.train.stratified, cfg.train.shuffle
    )

    save_results(
        preds,
        y,
        cfg.report.th,
        cfg.report.metrics_path,
        cfg.report.plot_path,
        cfg.train.seed,
    )


if __name__ == "__main__":
    main()
