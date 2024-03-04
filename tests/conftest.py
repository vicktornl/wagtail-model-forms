from django.conf import settings


def pytest_configure():
    settings.configure(
        CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}},
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": "db.sqlite",
            }
        },
        INSTALLED_APPS=[
            "wagtail.embeds",
            "wagtail.sites",
            "wagtail.users",
            "wagtail.snippets",
            "wagtail.documents",
            "wagtail.images",
            "wagtail.search",
            "wagtail.admin",
            "wagtail",
            "wagtail.contrib.routable_page",
            "modelcluster",
            "taggit",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.sitemaps",
            "django.contrib.staticfiles",
            "wagtail_model_forms",
        ],
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
            "wagtail.middleware.SiteMiddleware",
        ],
        SECRET_KEY="tests",
        STATIC_URL="/static/",
    )
