# Profiling

PFX provides a number of tools for easy profiling of SQL queries and python code by HTTP request.

## Profile command

To run your application in profile mode, the easiest way is to use the dedicated command:

```text
./manage.py profile
```

This is an alias to the `runserver` command, with profile mode automatically set.

By default, the logging configuration is overwritten and the profiling log level
is set to `DEBUG`. Everything else is set to `ERROR`
(the handler is forced to console output).

By default, output contains one entry per HTTP request, with execution time and
number of SQL requests (with SQL request execution time as a percentage of total time):

```text
PROFILE 2023-10-12 11:40:01,356
    GET /api/notifications?max_days=15&subset=offset&limit=2&offset=0 200 [30ms]
    SQL queries: 4 [6ms 20.18%]
PROFILE 2023-10-12 11:40:01,673
    GET /api/books?subset=offset&limit=16 200 [223ms]
    SQL queries: 3 [95ms 42.52%]
```

```{note}
If you run an ASGI application or if parallel HTTP requests can share the
same database connection, you can use the option `--db-router` to
force Django to use a new connection for each HTTP request:

```python
./manage.py profile --db-router
```

### SQL queries

You can display SQL queries by specifying a filter at the start of the HTTP path
(use `/` to logs queries for all paths):

```text
./manage.py profile --sql /api/books
…
PROFILE 2023-10-12 11:40:01,673
    GET /api/books?subset=offset&limit=16 200 [223ms]
    SQL queries: 3 [95ms 42.52%]
---
SELECT t.oid, typarray
FROM pg_type t
JOIN pg_namespace ns ON typnamespace = ns.oid
WHERE typname = 'hstore'
---
SELECT typarray
FROM pg_type
WHERE typname = 'citext'
---
SELECT count(books.id)
FROM "books"
INNER JOIN "authors" ON …
LEFT OUTER JOIN … ON (…)
WHERE (
    …)
GROUP BY …
ORDER BY …
---
SELECT …
FROM "books"
INNER JOIN "authors" ON …
LEFT OUTER JOIN … ON (…)
WHERE (
    …)
GROUP BY …
ORDER BY …
---
```

### cProfile

You can display the cProfile statistics by specifying a filter at the start of the HTTP path
(use `/` to logs queries for all paths):

```text
./manage.py profile --cprofile /api/books
…
PROFILE 2023-10-12 11:40:01,673
    GET /api/books?subset=offset&limit=16 200 [223ms]
    SQL queries: 3 [95ms 42.52%]

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      8/1    0.000    0.000    0.180    0.180 …/venv/lib/python3.8/site-packages/django/core/handlers/exception.py:44(inner)
      6/1    0.000    0.000    0.180    0.180 …/venv/lib/python3.8/site-packages/django/utils/deprecation.py:110(__call__)
        1    0.000    0.000    0.180    0.180 …/venv/lib/python3.8/site-packages/corsheaders/middleware.py:49(__call__)
        1    0.000    0.000    0.176    0.176 …/venv/lib/python3.8/site-packages/django/core/handlers/base.py:160(_get_response)
        1    0.000    0.000    0.167    0.167 …/venv/lib/python3.8/site-packages/django/views/generic/base.py:62(view)
        1    0.000    0.000    0.167    0.167 …/django-pfx/pfx/pfxcore/views/rest_views.py:1185(dispatch)
        1    0.001    0.001    0.167    0.167 …/django-pfx/pfx/pfxcore/decorator/rest.py:20(wrapper)
        1    0.000    0.000    0.166    0.166 …/books/books/views/books_rest_view.py:489(get_list)
        1    0.000    0.000    0.109    0.109 …/venv/lib/python3.8/site-packages/django/db/models/query.py:265(__iter__)
        1    0.000    0.000    0.109    0.109 …/venv/lib/python3.8/site-packages/django/db/models/query.py:1322(_fetch_all)
       88    0.000    0.000    0.109    0.001 …/venv/lib/python3.8/site-packages/django/db/models/query.py:97(__iter__)
        1    0.000    0.000    0.109    0.109 …/venv/lib/python3.8/site-packages/django/db/models/sql/compiler.py:1126(results_iter)
        1    0.000    0.000    0.109    0.109 …/venv/lib/python3.8/site-packages/django/db/models/sql/compiler.py:1147(execute_sql)
        4    0.083    0.021    0.083    0.021 {method 'execute' of 'psycopg2.extensions.cursor' objects}

```

### Custom logging configuration

You can use the `--keep-logging` parameter to disable automatic logging configuration.

```text
./manage.py profile --keep-logging
```

Your application's configuration will then be used. To display profiling information,
the `pfx.pfxcore.middleware.profiling` module must be at maximum logging level `DEBUG`.

```python
    'pfx.pfxcore.middleware.profiling': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    }
```

## Manual configuration

```{warning}
The SQL profiling works only if `settings.DEBUG = True`.
```

In some cases, you may want to use the profile mode outside the `profile` command.

To do this, you need to add the following middleware as the application's first middleware:

```python
DEBUG = True
MIDDLEWARE = [
    'pfx.pfxcore.middleware.ProfilingMiddleware',
    # … (your others middlewares)
]
```

```{note}
If you run an ASGI application or if parallel HTTP requests can share the
same database connection, you need the dedicated database router to
force Django to use a new connection for each HTTP request:

```python
DATABASE_ROUTERS = [
    'pfx.pfxcore.middleware.ProfilingDatabaseRouter'
]
```
```

The `PFX_PROFILING_SQL` and `PFX_PROFILING_CPROFILE` settings are optional
and correspond to the `--sql` and `--cprofile` parameters
of the `profile` command (set it to an empty string to disable):

```python
PFX_PROFILING_SQL = "/my-path"
PFX_PROFILING_CPROFILE = "/my-path"
```
