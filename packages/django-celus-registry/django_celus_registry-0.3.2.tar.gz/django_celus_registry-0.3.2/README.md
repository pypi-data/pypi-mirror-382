# Django Counter Registry
A simple scaper which download plublic data from [the registry](https://registry.countermetrics.org/) of [COUNTER project](https://www.countermetrics.org/)
and stores it as django models.

## Requirements
* Python 3.8+
* Django 4.2+
* requests

## Installation

Install using pip:
```
pip install django-counter-registry
```

Add it to your `INSTALLED_APPS` in your django settings:
```python
INSTALLED_APPS = (
    ...
    'django_counter_registry'
)
```

Fill models with up-to-date date
```
python manage.py shell -c 'from django_counter_registry.task import update_registry_models;update_registry_models()'
```
