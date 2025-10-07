# Template Integration Guide

## Automatic Integration (Recommended)

The package automatically provides a `base_site.html` template that extends Django's admin template and adds the Global Search button to the usertools section.

Simply install the package and it will work out of the box:

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django_global_search',  # Automatically adds the button
    # ...
]
```

The Global Search button will appear in the top right area of the admin interface, next to the user tools.

## Manual Integration

If you have a custom `admin/base_site.html` template, you can include the button manually:

```django
{% extends "admin/base_site.html" %}
{% load i18n %}

{% block usertools %}
{{ block.super }}
{% include 'global_search/button.html' %}
{% endblock %}
```

## Custom Button Placement

You can include the button anywhere in your admin templates:

```django
{% include 'global_search/button.html' %}
```

The button uses:
- Dynamic URL resolution via `{% url 'admin:global_search' %}`
- Internationalization via `{% trans "Global Search" %}`
- Inline styles that match Django admin theme

## URL Configuration

The global search URL is automatically registered as:
- URL name: `admin:global_search`
- Path: `<admin_url>/global-search/`

This works with any admin site URL prefix:
- `/admin/global-search/`
- `/custom-admin/global-search/`
- `/site/admin/global-search/`

## Internationalization

The button and search page support Django's i18n framework:

```python
# settings.py
LANGUAGE_CODE = 'ko'  # Korean
# or
LANGUAGE_CODE = 'en'  # English (default)
```

Default strings:
- "Global Search" - Button text
- "Search across all models..." - Input placeholder
- "No results found" - Empty state message

