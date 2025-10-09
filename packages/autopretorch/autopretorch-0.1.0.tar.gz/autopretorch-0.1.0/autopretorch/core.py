
import pandas as pd
import numpy as np
import torch
import joblib
import json
import datetime
import os
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

class AutoPreTorch:
    """
    AutoPreTorch - Extended version (research-ready)
    Features:
      - automatic numeric / categorical detection
      - imputation (mean / median / most_frequent)
      - scaling (standard / minmax)
      - encoding (label-like via category codes or one-hot)
      - differentiable embeddings for categorical features (optional)
      - conversion to torch tensors (with device)
      - Dataset / DataLoader creation
      - pipeline save / load (scalers/encoders + embeddings)
      - simple JSON logging + versioning
      - transform() method for inference
    """

    def __init__(self,
                 test_size: float = 0.2,
                 scale: str = "standard",       # 'standard', 'minmax', None
                 encode: str = "auto",          # 'label', 'onehot', 'auto', None
                 impute: str = "mean",          # 'mean', 'median', 'most_frequent', None
                 device: str = "cpu",
                 batch_size: int = 32,
                 shuffle: bool = True,
                 random_state: int = 42,
                 autograd_preprocess: bool = False,
                 embedding_size: int = 8,
                 log_dir: str = "autopretorch_logs"):
        self.test_size = test_size
        self.scale = scale
        self.encode = encode
        self.impute = impute
        self.device = device
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.random_state = random_state
        self.autograd_preprocess = autograd_preprocess
        self.embedding_size = embedding_size

        # internal state
        self.numeric_cols = []
        self.categorical_cols = []
        self.scalers = {}       # {col: scaler}
        self.imputers = {}      # {col: imputer}
        self.encoders = {}      # {col: OneHotEncoder or None}
        self.cat_maps = {}      # {col: categories list}
        self.embeddings = {}    # {col: torch.nn.Embedding}
        self.pipeline_version = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log = {}

        self.fitted = False
        self.train_loader = None
        self.test_loader = None

    # -------------------------
    # Public: fit_transform
    # -------------------------
    def fit_transform(self, df: pd.DataFrame, target_col: str):
        """
        Fit preprocessing on dataframe and return torch tensors:
        X_train, X_test, y_train, y_test (tensors on self.device)
        Also creates DataLoaders and writes a JSON log.
        """
        if target_col not in df.columns:
            raise ValueError(f"target_col '{target_col}' not in dataframe columns")

        X = df.drop(columns=[target_col]).copy()
        y = df[target_col].copy()

        # detect column types
        self.numeric_cols = X.select_dtypes(include=['int64','float64','int32','float32']).columns.tolist()
        self.categorical_cols = X.select_dtypes(include=['object','category','bool']).columns.tolist()

        # impute
        X = self._impute(X)

        # encode categorical
        X = self._encode_fit_transform(X)

        # scale numeric
        X = self._scale_fit_transform(X)

        # split
        X_train_df, X_test_df, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state
        )

        # to tensors
        X_train, X_test, y_train_t, y_test_t = self._to_tensor(X_train_df, X_test_df, y_train, y_test)

        # create dataloaders
        self.train_loader = self._create_dataloader(X_train, y_train_t)
        self.test_loader = self._create_dataloader(X_test, y_test_t)

        # logging
        self._write_log(target_col, df.shape[0])

        self.fitted = True
        return X_train, X_test, y_train_t, y_test_t

    # -------------------------
    # Public: transform (inference)
    # -------------------------
    def transform(self, df: pd.DataFrame):
        """
        Transform a dataframe using fitted pipeline. Returns torch tensor on device.
        """
        if not self.fitted:
            raise RuntimeError("Pipeline not fitted. Call fit_transform first or load_pipeline.")

        X = df.copy()
        # ensure columns present
        missing = [c for c in (self.numeric_cols + self.categorical_cols) if c not in X.columns]
        if missing:
            raise ValueError(f"Missing columns for transform: {missing}")

        # impute
        X = self._impute_transform(X)

        # encode
        X = self._encode_transform(X)

        # scale
        X = self._scale_transform(X)

        # convert
        X_tensor = torch.tensor(X.values, dtype=torch.float32, device=self.device)
        return X_tensor

    # -------------------------
    # Imputation helpers
    # -------------------------
    def _impute(self, X: pd.DataFrame):
        # numeric
        for col in self.numeric_cols:
            if self.impute is None:
                continue
            strategy = self.impute if self.impute in ['mean','median','most_frequent'] else 'mean'
            imputer = SimpleImputer(strategy=strategy)
            X[[col]] = imputer.fit_transform(X[[col]])
            self.imputers[col] = imputer
        # categorical
        for col in self.categorical_cols:
            if self.impute is None:
                # fill with unknown
                X[col] = X[col].fillna('@@MISSING@@')
            else:
                imputer = SimpleImputer(strategy='most_frequent')
                X[[col]] = imputer.fit_transform(X[[col]])
                self.imputers[col] = imputer
        return X

    def _impute_transform(self, X: pd.DataFrame):
        for col in self.numeric_cols:
            if col in self.imputers:
                X[[col]] = self.imputers[col].transform(X[[col]])
        for col in self.categorical_cols:
            if col in self.imputers:
                X[[col]] = self.imputers[col].transform(X[[col]])
            else:
                X[col] = X[col].fillna('@@MISSING@@')
        return X

    # -------------------------
    # Encoding helpers
    # -------------------------
    def _encode_fit_transform(self, X: pd.DataFrame):
        # For each categorical column decide encoder
        for col in list(self.categorical_cols):  # list(...) because we may expand columns on one-hot
            n_unique = int(X[col].nunique(dropna=False))
            if self.encode == 'onehot' or (self.encode == 'auto' and n_unique <= 10):
                # one-hot
                ohe = OneHotEncoder(sparse=False, handle_unknown='ignore')
                transformed = ohe.fit_transform(X[[col]])
                cat_cols = [f"{col}__{c}" for c in ohe.categories_[0].astype(str)]
                df_ohe = pd.DataFrame(transformed, columns=cat_cols, index=X.index)
                X = pd.concat([X.drop(columns=[col]), df_ohe], axis=1)
                self.encoders[col] = ('onehot', ohe, cat_cols)
            else:
                # label-like using category codes
                X[col] = X[col].astype('category')
                codes = X[col].cat.codes
                self.cat_maps[col] = list(X[col].cat.categories.astype(str))
                X[col] = codes
                if self.autograd_preprocess:
                    # create embedding layer
                    n_cat = len(self.cat_maps[col])
                    emb_dim = min(self.embedding_size, max(1, int(np.ceil(np.log2(n_cat+1))*2)))
                    emb = torch.nn.Embedding(n_cat, emb_dim)
                    self.embeddings[col] = emb
                else:
                    self.encoders[col] = ('label', None, None)
        return X

    def _encode_transform(self, X: pd.DataFrame):
        for col in list(self.categorical_cols):
            if col in self.encoders and self.encoders[col][0] == 'onehot':
                ohe = self.encoders[col][1]
                transformed = ohe.transform(X[[col]])
                cat_cols = self.encoders[col][2]
                df_ohe = pd.DataFrame(transformed, columns=cat_cols, index=X.index)
                X = pd.concat([X.drop(columns=[col]), df_ohe], axis=1)
            else:
                # label-like: map categories to codes based on trained categories
                categories = self.cat_maps.get(col, [])
                X[col] = X[col].astype(str).map({c: i for i, c in enumerate(categories)}).fillna(-1).astype(int)
                # if -1 (unknown), map to last index (or zero) — we choose 0 for simplicity
                X[col] = X[col].replace(-1, 0)
        return X

    # -------------------------
    # Scaling helpers
    # -------------------------
    def _scale_fit_transform(self, X: pd.DataFrame):
        for col in self.numeric_cols:
            if self.scale is None:
                continue
            if self.scale == 'standard':
                scaler = StandardScaler()
            else:
                scaler = MinMaxScaler()
            X[[col]] = scaler.fit_transform(X[[col]])
            self.scalers[col] = scaler
        return X

    def _scale_transform(self, X: pd.DataFrame):
        for col in self.numeric_cols:
            if col in self.scalers:
                X[[col]] = self.scalers[col].transform(X[[col]])
        return X

    # -------------------------
    # Tensor conversion & dataloader
    # -------------------------
    def _to_tensor(self, X_train_df, X_test_df, y_train, y_test):
        # ensure numeric numpy arrays
        X_train = torch.tensor(X_train_df.values, dtype=torch.float32, device=self.device)
        X_test = torch.tensor(X_test_df.values, dtype=torch.float32, device=self.device)
        y_train_t = torch.tensor(np.array(y_train).reshape(-1,1), dtype=torch.float32, device=self.device)
        y_test_t = torch.tensor(np.array(y_test).reshape(-1,1), dtype=torch.float32, device=self.device)
        return X_train, X_test, y_train_t, y_test_t

    class TabularDataset(Dataset):
        def __init__(self, X, y):
            self.X = X
            self.y = y
        def __len__(self):
            return self.X.shape[0]
        def __getitem__(self, idx):
            return self.X[idx], self.y[idx]

    def _create_dataloader(self, X, y):
        dataset = self.TabularDataset(X, y)
        return DataLoader(dataset, batch_size=self.batch_size, shuffle=self.shuffle)

    # -------------------------
    # Save / Load pipeline
    # -------------------------
    def save_pipeline(self, path: str = None):
        path = path or f"autopretorch_pipeline_{self.pipeline_version}.pt"
        payload = {
            'numeric_cols': self.numeric_cols,
            'categorical_cols': self.categorical_cols,
            'scalers': {k: joblib.dump(self.scalers[k], os.path.join(self.log_dir, f'scaler__{k}.joblib')) for k in self.scalers},
            'imputers': {k: joblib.dump(self.imputers[k], os.path.join(self.log_dir, f'imputer__{k}.joblib')) for k in self.imputers},
            'encoders_meta': {k: (self.encoders[k][0], self.encoders[k][2] if k in self.encoders else None) for k in self.encoders},
            'cat_maps': self.cat_maps,
            'pipeline_version': self.pipeline_version,
        }
        # Save embeddings separately if present
        emb_path = os.path.join(self.log_dir, f"embeddings_{self.pipeline_version}.pt")
        emb_state = {}
        for col, emb in self.embeddings.items():
            emb_state[col] = emb.state_dict()
        torch.save({'meta': payload, 'embeddings': emb_state}, path)
        # Also write JSON meta
        with open(path + ".json", "w") as f:
            json.dump({'meta': {'numeric_cols': self.numeric_cols, 'categorical_cols': self.categorical_cols, 'pipeline_version': self.pipeline_version}}, f, indent=2)
        return path

    def load_pipeline(self, path: str):
        data = torch.load(path, map_location=self.device)
        meta = data.get('meta', {})
        emb_state = data.get('embeddings', {})
        self.numeric_cols = meta.get('numeric_cols', [])
        self.categorical_cols = meta.get('categorical_cols', [])
        self.cat_maps = meta.get('cat_maps', {})
        # load scalers/imputers from files if paths were saved in meta (we saved via joblib in log_dir)
        # Re-create embedding layers and load state
        for col, state in emb_state.items():
            num_rows = state['weight'].shape[0]
            emb_dim = state['weight'].shape[1]
            emb = torch.nn.Embedding(num_rows, emb_dim)
            emb.load_state_dict(state)
            self.embeddings[col] = emb.to(self.device)
        self.fitted = True
        return self

    # -------------------------
    # Logging
    # -------------------------
    def _write_log(self, target_col, n_samples):
        self.log = {
            "version": self.pipeline_version,
            "timestamp": str(datetime.datetime.now()),
            "n_samples": int(n_samples),
            "numeric_cols": self.numeric_cols,
            "categorical_cols": self.categorical_cols,
            "scale": self.scale,
            "encode": self.encode,
            "impute": self.impute,
        }
        path = os.path.join(self.log_dir, f"autopretorch_log_{self.pipeline_version}.json")
        with open(path, "w") as f:
            json.dump(self.log, f, indent=2)
        return path
