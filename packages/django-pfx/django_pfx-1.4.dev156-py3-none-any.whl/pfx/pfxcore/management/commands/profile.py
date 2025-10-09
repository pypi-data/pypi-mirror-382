from django.conf import settings
from django.core.management.commands.runserver import (
    Command as RunserverCommand,
)


class Command(RunserverCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--keep-logging", dest="keep_logging", action='store_true')
        parser.add_argument(
            "--db-router", dest="db_router", action='store_true')
        parser.add_argument(
            "--sql", dest="sql_queries", default="", type=str)
        parser.add_argument(
            "--cprofile", dest="cprofile", default="", type=str)

    def run(self, *args, **options):
        """Runs the server with profile mode."""

        settings.DEBUG = True
        settings.MIDDLEWARE = [
            'pfx.pfxcore.middleware.ProfilingMiddleware',
        ] + settings.MIDDLEWARE
        if options['db_router']:
            settings.DATABASE_ROUTERS = [
                'pfx.pfxcore.middleware.ProfilingDatabaseRouter'
            ] + settings.DATABASE_ROUTERS
        settings.PFX_PROFILING_SQL = options['sql_queries']
        settings.PFX_PROFILING_CPROFILE = options['cprofile']
        if not options['keep_logging']:
            settings.LOGGING = {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'console': {
                        'format': 'PROFILE {asctime} {message}',
                        'style': '{',
                    }
                },
                'handlers': {
                    'console': {
                        'class': 'logging.StreamHandler',
                        'formatter': 'console',
                    },
                },
                'root': {
                    'handlers': ['console'],
                    'level': 'ERROR',
                    'propagate': False,
                },
                'loggers': {
                    'django': {
                        'handlers': ['console'],
                        'level': 'ERROR',
                        'propagate': False,
                    },
                    'pfx.pfxcore.middleware.profiling': {
                        'handlers': ['console'],
                        'level': 'DEBUG',
                        'propagate': False,
                    }}}
        super(Command, self).run(*args, **options)
