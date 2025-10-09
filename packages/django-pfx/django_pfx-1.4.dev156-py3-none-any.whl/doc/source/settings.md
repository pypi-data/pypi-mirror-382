# Settings
This page lists all the settings used by Django PFX.

## Base

### PFX_BASE_URL
Base url of your frontend application.
Not used directly by PFX, but can be used in email templates for instance.

### PFX_SITE_NAME
The name of your website, application and/or api.
Used in the email sent by pfx (welcome email, reset password, etc.)

### PFX_RESET_PASSWORD_URL
The url to set/reset password in your frontend application.
The url must include the `token` and `uidb64` parameters,
like so: `f'{PFX_BASE_URL}/define-password?token={token}&uidb64={uidb64}"`.

### PFX_MAX_LIST_RESULT_SIZE
The maximum size of list returned by PFX ListRestView services.
The goal is to avoid performance issues for huge database table.

### PFX_TEST_MODE

Enable test features.

One good way to automate this setting is to rely on manage.py parameter

To test if you launch test`./manage.py test` :
```python
import sys

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    PFX_TEST_MODE=True
```


## Authentication

### PFX_SECRET_KEY
The secret key used to cypher the JWT token.

### PFX_TOKEN_SHORT_VALIDITY
Validity for short-validity tokens (optional, default `{'hours': 12}`)

### PFX_TOKEN_LONG_VALIDITY
Validity for long-validity tokens (optional, default `{'days': 30}`)

### PFX_COOKIE_DOMAIN
The domain sent in the cookie.
Refer to [MDN documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#domaindomain-value)

### PFX_COOKIE_SECURE
Boolean, value that indicate that the cookie is sent only with https request.
Refer to [MDN documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#secure)

### PFX_COOKIE_SAMESITE
SameSite value of the cookie.
Can be `Strict`, `Lax`, `None`
Refer to [MDN documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#samesitesamesite-value)

## Authorisation

### PFX_FORCE_USER_FILTERED_QUERYSET
Force the use of a specific queryset that is segregated by user.
