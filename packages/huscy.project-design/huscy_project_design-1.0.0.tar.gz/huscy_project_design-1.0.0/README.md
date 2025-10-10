# huscy.project_design

![PyPi Version](https://img.shields.io/pypi/v/huscy-project_design.svg)
![PyPi Status](https://img.shields.io/pypi/status/huscy-project_design)
![PyPI Downloads](https://img.shields.io/pypi/dm/huscy-project_design)
![PyPI License](https://img.shields.io/pypi/l/huscy-project_design?color=yellow)
![Python Versions](https://img.shields.io/pypi/pyversions/huscy-project_design.svg)
![Django Versions](https://img.shields.io/pypi/djversions/huscy-project_design)


Huscy is a free open-source software solution for managing study participants in the context of human sciences.
The software is deliberately implemented in a generic manner to appeal to a wide user base, while considering all relevant aspects of data protection.
The strictly modular software architecture allows for easy integration of new requirements, enabling the software to be customized to individual needs at any time.



## Requirements

- Python 3.9+
- A supported version of Django

In this project, Django versions 4.2, 5.1 and 5.2 are tested using tox.



## Installation

To install `husy.project_design` simply run:

    pip install huscy.project_design

Add required apps to `INSTALLED_APPS` in your `settings.py`:

```python
INSTALLED_APPS = (
    ...

    'huscy.project_design.apps.HuscyApp',
    'huscy.projects.apps.HuscyApp',
    'huscy.users.apps.HuscyApp',
)
```

Hook the urls from this app into your global `urls.py`:

```python
urlpatterns = [
    ...
    path('', include('huscy.project_design.urls')),
]
```



## Development

Install PostgreSQL and create a database user called `huscy` and a database called `huscy`.

    sudo -u postgres createdb huscy
    sudo -u postgres createuser -d huscy
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE huscy TO huscy;"
    sudo -u postgres psql -c "ALTER USER huscy WITH PASSWORD '123';"

Check out the repository and start your virtual environment (if necessary).

Install dependencies:

    make install

Create database tables:

    make migrate

Run tests to see if everything works fine:

    make test
