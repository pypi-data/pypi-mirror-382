# Simple Site Search

A simple Django app for site search functionality with Django CMS integration. This package provides a clean, easy-to-use search interface that can be integrated into Django CMS projects.

## Features

- **Django CMS Integration**: Seamlessly integrates with Django CMS as an apphook
- **Pagination Support**: Built-in pagination for search results
- **Multi-language Support**: Supports internationalization with Django's i18n framework
- **Customizable Templates**: Easy to customize search result templates
- **API Integration**: Connects to external search APIs (like AddSearch)
- **Responsive Design**: Bootstrap-compatible templates

## Installation

Install the package using pip:

```bash
pip install simplesitesearch
```

## Configuration

### 1. Add to INSTALLED_APPS

Add `simplesitesearch` to your Django project's `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'simplesitesearch',
    # ... other apps
]
```

### 2. Required Settings

Add the following settings to your Django settings file:

```python
# Search API Configuration
SITE_SEARCH_API_BASE_URL = "https://api.addsearch.com/v1/search/"
SITE_SEARCH_SITE_KEY = "your-site-key-here"
SITE_SEARCH_API_KEY = "your-api-key-here"  # Optional, if required by your API
```

### 3. URL Configuration

Include the app's URLs in your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... other URL patterns
    path('search/', include('simplesitesearch.urls')),
    # ... other URL patterns
]
```

## Django CMS Integration

### 1. Create a Search Page

1. Log into your Django CMS admin
2. Go to **Django CMS** > **Pages**
3. Create a new page named "Search"
4. Translate the title and slug in all languages
5. Save and continue editing

### 2. Configure the Page

1. Go to **Advanced settings** of the search page
2. Set the **ID** to `'search'`
3. Set **APPLICATION** to "Site Search"
4. Save the page
5. Remove the page from the menu (uncheck "menu" in the table)
6. Publish the page in all languages

### 3. Access the Search

Your search functionality will be available at the URL you configured for the search page.

## Usage

### Basic Search

The search form accepts a `q` parameter for the search term:

```
/search/?q=your+search+term
```

### Pagination

The search results support pagination with a `page` parameter:

```
/search/?q=your+search+term&page=2
```

### Honeypot Protection

The search includes basic honeypot protection. If a `message` parameter is present, the search will not execute.

## Customization

### Templates

The package includes two main templates:

- `simplesitesearch/search_results.html` - Main search results template
- `simplesitesearch/pagination.html` - Pagination template

You can override these templates in your project by creating templates with the same names in your template directory.

### Styling

The templates use Bootstrap classes and can be easily customized with CSS. The main CSS classes used are:

- `.pagination` - Pagination container
- `.search_query` - Search query display
- `.search_results` - Results count display
- `.wrapper_single_result` - Individual result container

## API Response Format

The search expects the API to return JSON in the following format:

```json
{
    "total_hits": 42,
    "hits": [
        {
            "title": "Page Title",
            "url": "https://example.com/page/",
            "highlight": "Search term highlighted content..."
        }
    ]
}
```

## Requirements

- Python 3.6+
- Django 2.2+
- django-cms 3.2+
- requests 2.25.0+

## Development

### Local Development

1. Clone the repository
2. Install in development mode:
   ```bash
   pip install -e .
   ```

### Testing

Run the tests with:

```bash
python manage.py test simplesitesearch
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions, please open an issue on the [GitHub repository](https://github.com/yourusername/simplesitesearch/issues).

## Changelog

### 1.0.0
- Initial release
- Django CMS integration
- Pagination support
- Multi-language support
- Basic search functionality

### 1.0.3
- Allow python version 3.6, 3.7

### 1.0.3
- Allow Django version 2.2


