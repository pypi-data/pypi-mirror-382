# Internationalisation

## Translated strings

Use Django's standard way of translating strings (verbose name, choices values, messages, ...).
PFX will use the translated values according to the requested language.

## Specify available languages

In Django, `USE_I18N` must be `True` to use internationalization. Use `LANGUAGE_CODE` to set default locale.

You can optionally set `USE_L10N` to `True` (see Django documentation).

In Addition, you can set the list of available languages for web services with `LANGUAGES`:
```python
LANGUAGES = [
    ('fr', "French"),
    ('en', "English"),
]
```

You can use language only code of language and country.

Service responses will use the first language of `Accept-Language` present in `LANGUAGES`.
Use `X-Custom-Language` to force the use of a specific language.

## LocaleRestView

The `LocaleRestView` exposes a service on `/locales/languages` which returns the list of
available languages.

## LocaleMiddleware

To enable internationalization in services, you have to add `'pfx.pfxcore.middleware.LocaleMiddleware'`
in the `MIDDLEWARE` list.

This middleware will use:
* `LANGUAGES`, `LANGUAGE_CODE`, `Accept-Language` and `X-Custom-Language` to set the language.
* `TIME_ZONE` and `X-Custom-Timezone` sot set the timezone.

You can replace it by a custom middleware if you need another specific behavior.
