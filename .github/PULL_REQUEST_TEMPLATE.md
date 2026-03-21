## Summary

## Validation

- [ ] `python -m py_compile metaflow_clockwork/*.py tests/test_*.py`
- [ ] `python -m unittest discover -s tests -p 'test_*.py' -v`
- [ ] relevant CLI smoke path, if behavior changed

## Checklist

- [ ] docs updated where needed
- [ ] no secrets or local-only artifacts added
- [ ] authority boundaries remain intact
