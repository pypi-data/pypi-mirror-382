# Django Global Search

**Global search for Django Admin** - Search across all registered models with permissions and search_fields support.

## Overview

Django Global Search adds a unified search interface to Django Admin, allowing you to search across multiple models simultaneously. It respects existing Django Admin configurations including `search_fields`, permissions, and custom querysets.

## Key Features

- **Zero Configuration**: Works out of the box with existing Django Admin setup
- **Permission-Aware**: Respects Django's model-level and object-level permissions
- **Search Fields Integration**: Uses your existing `ModelAdmin.search_fields` configuration
- **Timeout Protection**: Prevents slow queries from blocking the entire search
- **Configurable**: Customize search behavior per model or globally

## Quick Example

After installation, simply add `django_global_search` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django_global_search',  # Add after django.contrib.admin
    # ... your other apps
]
```

That's it! Visit `/admin/global-search/` to start searching across all your models.

## How It Works

1. **Automatic Integration**: The library automatically extends Django's default admin site
2. **Respects Permissions**: Only searches models the user has view permission for
3. **Uses Existing Config**: Leverages your existing `search_fields` configuration
4. **Smart Results**: Groups results by app and model for easy navigation

## Screenshots

### Global Search Interface
![Global Search Interface](./media/admin_search_page.png)

*Search across all models with permission-based filtering and model selection*

### Search Results
![Search Results](./media/admin_search_result_page.png)

*Results grouped by app and model with direct links to detail and changelist views*

## Requirements

- Python 3.9+
- Django 4.2+

## Next Steps

- [Installation Guide](installation.md) - Install and set up the package
- [Quick Start](quickstart.md) - Get started in 5 minutes
- [Configuration](configuration.md) - Customize search behavior

## Project Status

!!! warning "Early Development"
    This project is in under active development. APIs may change in future releases.

## License

This project is open source. See the repository for license details.
