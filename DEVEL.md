# Developer information

## Dependences

You can install the development dependences by running

```
pip install -r requirements-dev.txt
```

## Installing

To sdist-package, install and test your project against Python2.6 and Python2.7, just type:
```
tox
```

## Running tests

```
paver test all
```

## Localy installing the package

```
pip install -e .
```

## Creating source distributions

```
python setup.py sdist
```

## Creating binary distributions (Wheels)a

```
python setup.py bdist_wheel --universal
```

## Creating both soure & binary distributions (Wheels)a

```
python setup.py sdist bdist_wheel --universal
```

## Uploading the distribution to PyPi

```
twine upload dist/*
```

You can specify the version to upload:

```
twine upload dist/*1.0*
```

You should first use the test repository:

```
twine upload -r pypitest dist/*1.0*
```

## Additional info

Have a look to the Packaging and Distributing Projects tutorial:

https://packaging.python.org/distributing/

The package has been generated following seafisk's Python Project Template:

https://github.com/seanfisk/python-project-template

