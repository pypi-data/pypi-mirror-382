from config import DB_PATH

# Based on https://abdus.dev/posts/django-orm-standalone/


def init_django():
    import django
    from django.conf import settings

    if settings.configured:
        return

    settings.configure(
        DEFAULT_AUTO_FIELD="django.db.models.AutoField",
        INSTALLED_APPS=[
            "db",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": DB_PATH,
            }
        },
    )
    django.setup()


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    init_django()
    execute_from_command_line()
