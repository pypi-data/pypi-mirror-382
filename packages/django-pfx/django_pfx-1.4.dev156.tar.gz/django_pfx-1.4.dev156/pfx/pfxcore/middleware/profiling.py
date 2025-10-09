import cProfile
import io
import logging
import pstats
from contextvars import ContextVar
from time import monotonic_ns

from django.db import connection, connections
from django.utils.connection import BaseConnectionHandler
from django.utils.deprecation import MiddlewareMixin

import sqlparse

from pfx.pfxcore.settings import settings

logger = logging.getLogger(__name__)
rid = ContextVar('var')


class ProfilingDatabaseRouter:
    def db_for_read(self, model, **hints):
        return rid.get('default')

    def db_for_write(self, model, **hints):
        return rid.get('default')


class ProfilingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._profile = None
        if settings.PFX_PROFILING_CPROFILE and request.path.startswith(
                settings.PFX_PROFILING_CPROFILE):
            request._profile = cProfile.Profile()
            request._profile.enable()

        request._db_router = False
        if 'ProfilingDatabaseRouter' in ','.join(settings.DATABASE_ROUTERS):
            request._db_router = True
            # Avoid RuntimeError: dictionary changed size during iteration
            BaseConnectionHandler.__iter__ = lambda s: iter(dict(s.settings))
            request._rid = str(id(request))
            settings.DATABASES[request._rid] = settings.DATABASES[
                connection._alias
            ]
            rid.set(request._rid)

        request._start_time = monotonic_ns()

    def process_response(self, request, response):
        req_time = (monotonic_ns() - request._start_time) / 1000000

        if request._profile:
            request._profile.disable()
            s = io.StringIO()
            sortby = pstats.SortKey.CUMULATIVE
            ps = pstats.Stats(request._profile, stream=s).sort_stats(sortby)
            ps.print_stats()

        if request._db_router:
            queries = connections[request._rid].queries[:]
        else:
            queries = connection.queries[:]
        sqltime = 0
        sqls = []
        for query in queries:
            sqltime += float(query["time"]) * 1000
            sqlquery = sqlparse.format(
                query['sql'], reindent=True, wrap_after=160)
            if settings.PFX_PROFILING_SQL and request.path.startswith(
                    settings.PFX_PROFILING_SQL):
                sqls.append(f"\n---\n{sqlquery}")
        if sqls:
            sqls.append("\n---")

        sqltime_p = 100 * sqltime / req_time
        logger.debug(
            f"\n    {request.method} {request.get_full_path()} "
            f"{response.status_code} [{req_time:.0f}ms]"
            f"\n    SQL queries: {len(queries)} "
            f"[{sqltime:.0f}ms {sqltime_p:.2f}%]"
            f"{''.join(sqls)}"
            + (request._profile and f"\n{s.getvalue()}" or ""))

        if request._db_router:
            connections[request._rid].close()
            settings.DATABASES.pop(request._rid)
        return response
