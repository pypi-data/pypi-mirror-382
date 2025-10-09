# How to integrate with Flask-Admin

Make sure your Flask app's Jinja environment is configured to load templates from at least the sources listed below. 
Then initialise Flask-Admin and govuk-flask-admin appropriately, making sure to pass the GOV.UK Frontend Theme to 
Flask-Admin.

```python
from flask import Flask
from jinja2 import PackageLoader, ChoiceLoader, PrefixLoader

from flask_admin import Admin
from govuk_flask_admin import GovukFlaskAdmin, GovukFrontendTheme

app = Flask(...)
app.jinja_options = {
    "loader": ChoiceLoader(
        [
            PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}),
            PrefixLoader({"govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf")}),
            PackageLoader("govuk_flask_admin"),
        ]
    )
}

admin = Admin(app, theme=GovukFrontendTheme())
govuk_flask_admin = GovukFlaskAdmin(app)
```

All of your SQLAlchemy model fields should derive from govuk-flask-admin's `GovukModelView`, not from Flask-Admin's 
`sqla.ModelView`.

## Developing this extension

### Rebuilding GOV.UK Frontend assets

GOV.UK Flask Admin uses and extends the GOV.UK Frontend CSS and JS in order to add functionality required to display information and action dense admin pages.

These assets are compiled using Flask-Vite.

#### One-off setup

1. Install Node LTS (currently v20)
2. Run `flask vite install`
3. Run `flask vite build` to compile GOV.UK Frontend assets and copy them into `govuk_flask_admin/static`
4. Commit the newly compiled assets.
