from django.apps import AppConfig


class PaymentsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'paymentsApp'

    def ready(self):
        import paymentsApp.signals  # Ensure signals are registered