# Authentication

Django PFX offers services and middlewares for managing user authentication in your API.
These services replicate some of the functionalities provided by the {mod}`django.contrib.auth`
package but in the form of RESTful services.
They utilize the same user model and authentication backend features,
including password validation and hashing.

## User Model

You have the option to use the standard Django User with {class}`pfx.pfxcore.models.PFXUser`
(which is a {class}`django.contrib.auth.models.User` with PFX required mixins):

```python
AUTH_USER_MODEL = 'pfxcore.PFXUser'
```

But you may prefer to use your own model. To do this, create your own user class.

You have 2 options:

```python
from pfx.pfxcore.models import AbstractPFXBaseUser

class MyUser(AbstractPFXBaseUser):
    # Equivalent of django.contrib.auth.models.AbstractBaseUser for PFX.
    #
    # Minimal user, you have to manage the USERNAME_FIELD by yourself,
    # and you have to add django.contrib.auth.models.PermissionsMixin
    # if you want to use the permission system.
    pass
```

```python
from pfx.pfxcore.models import AbstractPFXUser

class MyUser(AbstractPFXUser):
    # Equivalent of django.contrib.auth.models.AbstractUser for PFX.
    #
    # This is the same as using pfxcore.PFXUser, but you can add your
    # custom fields.
    pass

```

Then, define the model in your settings:

```python
AUTH_USER_MODEL = 'myapp.MyUser'
```

## Authentication Modes

There are two authentication modes available: cookie and bearer token. You can activate either or both by enabling the following middlewares:

* {class}`pfx.pfxcore.middleware.AuthenticationMiddleware` (bearer token)
* {class}`pfx.pfxcore.middleware.CookieAuthenticationMiddleware` (cookie)

### Token Validity

You can customize token validity by configuring these parameters:

* `PFX_TOKEN_SHORT_VALIDITY`: Validity for short-validity tokens (optional, default `{'hours': 12}`)
* `PFX_TOKEN_LONG_VALIDITY`: Validity for long-validity tokens (optional, default `{'days': 30}`)

### Cookie Settings

To use the {class}`pfx.pfxcore.middleware.CookieAuthenticationMiddleware`, you need to configure the following settings:

* `PFX_COOKIE_DOMAIN`: The cookie domain
* `PFX_COOKIE_SECURE`: `Secure` attribute of the cookie (`True`/`False`)
* `PFX_COOKIE_SAMESITE`: `SameSite` attribute of the cookie (`'Strict'`/`'Lax'`/`'None'`)

See the [MDN Website](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies) for more details.

### Temporary bans

Users will be temporarily banned after several unsuccessful login attempts.

In the event of a temporary ban, login services will respond with the HTTP code `429` and
the `Retry-After` header.

#### Settings

* `PFX_LOGIN_BAN_FAILED_NUMBER`: The number of failed login attempts before banning. To deactivate the ban completely, set `0` (optional, default `5`).
* `PFX_LOGIN_BAN_SECONDS_START`: The number of seconds for the first ban (optional, default `60`).
* `PFX_LOGIN_BAN_SECONDS_STEP`: The number of seconds to be added to the previous ban for consecutive bans (optional, default `60`).

### Multifactor Authentication
Multifactor authentication can be enabled in django-pfx Authentication API.

PFX currently provides MFA with One Time Password (OTP), compatible with FreeOTP,
Google Authenticator and other OTP app.

To enable this feature, install django-pfx with otp.

```bash
pip install django-pfx[otp]
```

Then the user class must use the {class}`pfx.pfxcore.models.OtpUserMixin`.

```python
from pfx.pfxcore.models import PFXUser, OtpUserMixin

class MyUser(OtpUserMixin, PFXUser):
    pass
```

or

```python
from pfx.pfxcore.models import AbstractPFXBaseUser, OtpUserMixin

class MyUser(OtpUserMixin, AbstractPFXBaseUser):
    pass
```

#### Settings

* `PFX_TOKEN_OTP_VALIDITY`: Validity for OTP tokens (corresponds to the maximum time to enter
  an OTP code after logging in with a password) (optional, default `{'minutes': 15}`)
* `PFX_HOTP_CODE_VALIDITY`: Validity of HOTP codes in minutes (used to send code by email) (optional, default `15`).
* `PFX_OTP_VALID_WINDOW`: TOTP valid window (optional, default `1`).
  According to [RFC 6238 section 5.2](https://www.ietf.org/rfc/rfc6238.html#section-5.2).
* `PFX_OTP_IMAGE`: An image https URL used by FreeOTP. See [FreeOTP URI](https://github.com/npmccallum/freeotp-android/blob/master/URI.md).
* `PFX_OTP_COLOR`: A brand color (in RRGGBB format) for used by FreeOTP. See [FreeOTP URI](https://github.com/npmccallum/freeotp-android/blob/master/URI.md).

The user can then enable or disable the OTP auth using the [services documented below](#enable-mfa-otp).

## Services

### Login
A login rest services with a `mode` parameter to choose between JWT bearer token or cookie authentication.
In cookie mode, the JWT token is saved in an HTTP-only cookie.

```{mermaid}

   sequenceDiagram
      participant App
      participant API
      App->>API: POST /auth/login
      alt Authentication success
        API->>App: 200 OK + cookie
      else Authentication failed
        API->>App: 401 Unautorized
      end

```

**Request :** `POST` `/auth/login?mode=<mode>`

**Request body:**

| Field       | Description                         |
|-------------|-------------------------------------|
| username    | the username                        |
| password    | the password                        |
| remember_me | If true, use a long validity token. |

**Responses :**

* `HTTP 401` if the credentials are incorrect
* `HTTP 200` with the following body

| Field | Description                            |
|-------|----------------------------------------|
| token | the jwt token. (only if mode is 'jwt') |
| user  | the user object                        |


### Login + TOTP
If the user has enabled the TOTP login, the process is the same as above for the first step,
except that the login service returns a temporary JWT token valid only for the otp services.

```{mermaid}

   sequenceDiagram
      participant App
      participant API
      App->>API: POST /auth/login
      alt Login success
        API->>App: 200 OK
        note left of API: temporary jwt token
        App->>API: POST /auth/otp/login
        note right of App: temporary jwt token + OTP token in body.
        alt OTP success
            API->>App: 200 OK
            note left of API: JWT token in cookie or in body <br/> + user in body
        else OTP failed
            API->>App: 401 Unautorized
        end
      else Login failed
        API->>App: 401 Unautorized
      end

```

**Request :** `POST` `/auth/login?mode=<mode>`

**Request body:**

| Field       | Description                         |
|-------------|-------------------------------------|
| username    | the username                        |
| password    | the password                        |
| remember_me | If true, use a long validity token. |

**Responses :**

* `HTTP 401` if the credentials are incorrect
* `HTTP 200` with the following body

| Field | Description           |
|-------|-----------------------|
| token | a temporary jwt token |


**Request :** `POST` `/auth/otp/login?mode=<mode>`

**Request body:**

| Field       | Description                         |
|-------------|-------------------------------------|
| token       | the temporary jwt token             |
| otp         | the one time password (TOTP)        |

**Responses :**

* `HTTP 401` if the temporary jwt token is incorrect
* `HTTP 403` if the otp is incorrect
* `HTTP 200` with the following body

| Field | Description                            |
|-------|----------------------------------------|
| token | the jwt token. (only if mode is 'jwt') |
| user  | the user object                        |

### Enable MFA OTP
Services to enable the MFA with OTP.
You have to call first the `setup-uri` service to get the URI,
encode it as a QR code and present it in the UI of your software.
Then user then scans this QR code to add the OTP secret to his OTP App.
Finally, the `enable` service must be called with an OTP code retrieved
in the OTP App to confirm the activation.

**Request :** `GET` `/auth/otp/setup-uri`

**Responses :**

* `HTTP 400` if the otp is already enabled
* `HTTP 200` with the following body

| Field     | Description                           |
|-----------|---------------------------------------|
| setup_uri | the uri to enable the OTP application |

**Request :** `PUT` `/auth/otp/enable`

**Request body:**

| Field       | Description                           |
|-------------|---------------------------------------|
| otp_code    | the otp code retrieved in the OTP app |

**Responses :**

* `HTTP 422` if the otp code is invalid
* `HTTP 200` if the otp code is valid

### Disable MFA OTP
A service to disable the MFA with OTP.

**Request :** `PUT` `/auth/otp/disable`

**Request body:**

| Field       | Description                           |
|-------------|---------------------------------------|
| otp_code    | the otp code retrieved in the OTP app |

**Responses :**

* `HTTP 422` if the otp code is invalid
* `HTTP 200` if the otp code is valid


### Logout
A service that deletes the authentication cookie if it exists.

**Request :** `GET` `/auth/logout`

**Responses :** `HTTP 200` OK with a success message.


### Change Password
A service to change the password of an authenticated user.

**Request :** `POST` `/auth/change-password`

**Request body :**

| Field        | Description          |
|--------------|----------------------|
| old_password | the current password |
| new_password | the new password     |

**Responses :**
* `HTTP 422` if any validation error
* `HTTP 200` OK with a success message.

### Forgotten Password
A service that allows users to request a password reset. This service sends an email to the user containing
a link to a "set password" page, which your frontend software must implement.

You must set `PFX_RESET_PASSWORD_URL` in your settings to define this "set password" link.
The link must include the `token` and `uidb64` parameters,
like so: `https://example.com/reset-password?token={token}&uidb64={uidb64}`.
Your reset page should then call the "set password" service with these two parameters.

You can override this class if you need to customize the email templates.
Refer to {class}`pfx.pfxcore.views.ForgottenPasswordView` for more details.

**Request :** `POST` `/auth/forgotten-password`

**Request body :**

| Field | Description              |
|-------|--------------------------|
| email | the user's email address |

**Responses :**
* `HTTP 200` OK with a success message.
* `HTTP 422` Error if the email parameter is not an email address

### Sign Up
A service that allows visitors to sign up.
This service sends a welcome email to the user containing a link to a "set password" page,
which your frontend software must implement.

You must set `PFX_RESET_PASSWORD_URL` in your settings to define this "set password" link.
The link should include the `token` and `uidb64` parameters,
like so: `https://example.com/reset-password?token={token}&uidb64={uidb64}`.
Your reset page should then call the "set password" service with these two parameters.

You can override this class if you need to customize the user or email templates.
Refer to {class}`pfx.pfxcore.views.SignupView` for more details.

**Request :** `POST` `/auth/signup`

**Request body :**

| Field      | Description              |
|------------|--------------------------|
| first_name | the user's first name    |
| last_name  | the user's  last name    |
| username   | the user name            |
| email      | the user's email address |

**Responses :**
* `HTTP 422` if there are validation error.
* `HTTP 200` OK with a success message.

### Set Password
A service for setting the password using a UID and a token provided
in the email sent by the "forgotten password" or "sign up" services.

**Request :** `POST` `/auth/set-password`

**Request body :**

| Field     | Description                                                   |
|-----------|---------------------------------------------------------------|
| uidb64    | the uid in base64 sent in the set/reset password link         |
| token     | the reset password token sent in the set/reset password link  |
| password  | the new password                                              |
| autologin | Automatically logs the user in upon successful authentication |

_Autologin value must match the login's `mode` parameters (`cookie` or `jwt`)._

**Responses :**
* `HTTP 401` if the token or uidb64 is invalid
* `HTTP 422` if there are validation error.
* `HTTP 200` OK with a success message.

### Validate User Token
You can use this service to validate the token and `uidb64` before the
"Set Password" service is called, such as when a user opens the "set password"
page of your frontend application.

**Request :** `POST` `/auth/validate-user-token`

**Request body :**

| Field     | Description                                                   |
|-----------|---------------------------------------------------------------|
| uidb64    | the uid in base64 sent in the set/reset password link         |
| token     | the reset password token sent in the set/reset password link  |


**Responses :**
* `HTTP 422` if the data are invalid
* `HTTP 200` OK with a success message.
