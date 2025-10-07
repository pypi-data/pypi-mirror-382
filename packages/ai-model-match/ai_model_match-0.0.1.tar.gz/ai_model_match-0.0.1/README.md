# ai-model-match

TBD

## Installation

```bash
pip install ai-model-match
```

## Development

```bash
python3 -m pip install --upgrade build twine
python3 -m build
# To test on https://test.pypi.org/
twine upload --repository testpypi dist/*
pip install -i https://test.pypi.org/simple ai-model-match

# Test installation
pip install -i https://test.pypi.org/simple ai-model-match

# Push on Pypi https://pypi.org/
twine upload dist/*

```
