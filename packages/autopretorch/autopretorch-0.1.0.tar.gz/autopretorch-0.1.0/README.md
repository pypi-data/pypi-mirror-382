
# AutoPreTorch (Extended)

AutoPreTorch is an extended preprocessing library for PyTorch workflows.
Features:
- Imputation, scaling, encoding
- Differentiable embedding support (research mode)
- Pipeline logging and versioning
- Easy save/load for pipelines

Installation:
```
pip install .
```

Usage:
```python
from autopretorch import AutoPreTorch
auto = AutoPreTorch(scale='standard', encode='auto', impute='mean', autograd_preprocess=False)
X_train, X_test, y_train, y_test = auto.fit_transform(df, target_col='target')
```
