# Django XLAdmin Enhanced

A modern, enhanced version of Django XAdmin - a powerful admin interface for Django applications.

## Features

- **Modern UI**: Clean and responsive admin interface
- **Plugin System**: Extensible plugin architecture
- **Advanced Filtering**: Powerful filtering and search capabilities
- **Import/Export**: Built-in data import/export functionality
- **Permissions**: Fine-grained permission control
- **Customizable**: Highly customizable admin interface
- **Multi-language**: Internationalization support
- **Dashboard**: Customizable dashboard with widgets

## Installation

```bash
pip install django-xladmin-enhanced
```

## Quick Start

1. Add `xladmin` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'xladmin',
    'crispy_forms',
    'import_export',
    'reversion',
    # ...
]
```

2. Replace Django's default admin in your main `urls.py`:

```python
import xladmin
xladmin.autodiscover()

from xladmin.plugins import xversion
xversion.register_models()

urlpatterns = [
    path('xladmin/', xladmin.site.urls),
    # ...
]
```

3. Create an admin configuration file `adminx.py` in your app:

```python
import xladmin
from .models import YourModel

class YourModelAdmin(object):
    list_display = ['field1', 'field2', 'field3']
    search_fields = ['field1', 'field2']
    list_filter = ['field3']

xladmin.site.register(YourModel, YourModelAdmin)
```

4. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Configuration

### Settings

Add these settings to your Django settings file:

```python
# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# XLAdmin Settings
XLADMIN_TITLE = 'Your Admin Title'
XLADMIN_FOOTER_TITLE = 'Your Footer'
```

### Plugins

XLAdmin Enhanced comes with several built-in plugins:

- **Actions**: Batch actions for model instances
- **Filters**: Advanced filtering options
- **Bookmarks**: Save and manage bookmarks
- **Export**: Export data in various formats
- **Import**: Import data from files
- **Charts**: Display charts and graphs
- **Images**: Image handling and thumbnails
- **RelField**: Related field enhancements
- **Refresh**: Auto-refresh functionality
- **Details**: Enhanced detail views
- **Editable**: Inline editing capabilities
- **Relate**: Related object management
- **Portal**: Dashboard portal widgets
- **QuickForm**: Quick form creation
- **Wizard**: Multi-step form wizard
- **Ajax**: AJAX functionality
- **Aggregation**: Data aggregation tools
- **Mobile**: Mobile-responsive interface
- **Passwords**: Password management
- **Multiselect**: Multiple selection widgets
- **Themes**: Theme customization
- **Language**: Multi-language support
- **QuickFilter**: Quick filtering options
- **Sortable**: Drag-and-drop sorting
- **Topnav**: Top navigation enhancements
- **Portal**: Dashboard customization

## Advanced Usage

### Custom Plugins

You can create custom plugins by extending the base plugin classes:

```python
from xladmin.plugins import BaseAdminPlugin

class MyCustomPlugin(BaseAdminPlugin):
    def init_request(self, *args, **kwargs):
        # Plugin initialization logic
        pass
```

### Theming

Customize the admin interface appearance:

```python
class MyModelAdmin(object):
    # Custom CSS and JS
    class Media:
        css = {
            'all': ('my_admin.css',)
        }
        js = ('my_admin.js',)
```

## Requirements

- Python >= 3.8
- Django >= 3.2
- django-crispy-forms >= 1.14.0
- django-import-export >= 2.8.0
- django-reversion >= 5.0.0

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please file an issue on the GitHub repository.

## Changelog

### Version 1.0.0
- Initial release
- Enhanced UI and UX
- Modern plugin system
- Improved performance
- Better documentation