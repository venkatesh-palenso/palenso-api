from django.apps import AppConfig


class DbConfig(AppConfig):
    name = 'palenso.db'

    def ready(self):
        """Import signals when the app is ready"""
        import palenso.db.signals.base
