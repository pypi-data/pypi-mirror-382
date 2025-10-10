# pve-cloud-backup

python package and docker image that form the base for backing up pve cloud lxcs/qms/k8s.

## Releasing to pypi

```bash
pip install build twine
rm -rf dist
python3 -m build
python3 -m twine upload dist/*
```

## Docker hub

```bash
VERSION=$(grep -E '^version *= *"' pyproject.toml | sed -E 's/^version *= *"(.*)"/\1/')
docker build --build-arg PY_PKG_VERSION=$VERSION -t tobiashvmz/pve-cloud-backup:$VERSION .
docker push tobiashvmz/pve-cloud-backup:$VERSION
```