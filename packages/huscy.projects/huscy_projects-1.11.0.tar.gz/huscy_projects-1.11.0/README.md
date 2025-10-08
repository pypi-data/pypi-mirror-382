# huscy.projects

![PyPi Version](https://img.shields.io/pypi/v/huscy-projects.svg)
![PyPi Status](https://img.shields.io/pypi/status/huscy-projects)
![PyPI Downloads](https://img.shields.io/pypi/dm/huscy-projects)
![PyPI License](https://img.shields.io/pypi/l/huscy-projects?color=yellow)
![Python Versions](https://img.shields.io/pypi/pyversions/huscy-projects.svg)
![Django Versions](https://img.shields.io/pypi/djversions/huscy-projects)
[![Coverage Status](https://coveralls.io/repos/bitbucket/huscy/projects/badge.svg?branch=master)](https://coveralls.io/bitbucket/huscy/projects?branch=master)



## Requirements

- Python 3.8+
- A supported version of Django

Tox tests on Django versions 4.2, 5.0 and 5.1.



## Installation

To install `husy.projects` simply run:

	pip install huscy.projects


Add `huscy.projects` and further required apps to `INSTALLED_APPS` in your settings module:

```python
INSTALLED_APPS = (
	...
	'guardian',
	'rest_framework',

	'huscy.projects',
)
```

Add Django Guardian ObjectPermissionBackend to AUTHENTICATION_BACKENDS

```python
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)
```

Hook the urls from `huscy.projects` into your urls.py:

```python
urlpatterns = [
    ...
	path('/api/', include('huscy.projects.urls')),
]
```

Create `huscy.projects` database tables by running:

	python manage.py migrate



## Development

Install PostgreSQL and create a database user called `huscy` and a database called `huscy`.

	sudo -u postgres createdb huscy
	sudo -u postgres createuser -d huscy
	sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE huscy TO huscy;"
	sudo -u postgres psql -c "ALTER USER huscy WITH PASSWORD '123';"

Checking out the repository start your virtual environment (if necessary).

Install all development and test dependencies:

	make install

Create Database tables:

	make migrate

Run tests to see if everything works fine:

	make test
