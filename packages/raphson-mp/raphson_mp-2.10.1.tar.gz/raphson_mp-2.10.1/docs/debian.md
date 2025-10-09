# Debian packages

## Building packages

If you are not on Debian or on a different version, use distrobox:
```
distrobox create --image debian:bookworm --name debian
distrobox enter debian
```

Install build dependencies:
```
sudo apt install dpkg-dev debhelper dh-python pybuild-plugin-pyproject python3-hatchling
dpkg-buildpackage -tc --no-sign
```

The -tc option ensures temporary data is deleted after building. The built package is placed in the parent directory of the repository.
