# Django Yivi auth

A Django app to allow users to authenticate with Yivi, using the [proxy flow](https://github.com/privacybydesign/yivi-frontend-packages#talking-to-irma-server-through-a-proxy) (so not using the [signed request flow](https://github.com/privacybydesign/yivi-frontend-packages#talking-to-irma-server-directly-with-signed-request) with JWTs).

## Installation

Add `yivi_auth` to your `INSTALLED_APPS` setting.

```python
INSTALLED_APPS = [
    ...,
    'yivi_auth',
]
```

Add the `yivi_auth` urls to your `urls.py` file.

```python
from django.urls import path, include

urlpatterns = [
    ...,
    path("auth/", include("yivi_auth.urls")),
]
```

Configure a [Yivi server](https://irma.app/docs/irma-server/) in your `settings.py` file. Currently, only token authentication is supported.

```python
YIVI_SERVER_HOSTNAME = "http://yivi.example.com"
YIVI_SERVER_TOKEN = "foobar"
```

## Usage

### Django view
When a Yivi disclosure session is performed, a Django signal `yivi_auth.signals.yivi_session_done` is sent.
This signal contains the result of the session, the Yivi session object and the original yivi session that was started.
You can connect a function to this signal to handle the result of the session.
Note that you can use the `original_path` and `request` attributes of the Yivi session to check if the session was started from a specific view.

```python
from django.dispatch import receiver
from yivi_auth.signals import yivi_session_done

yivi_login_request = {
    "@context": "https://irma.app/ld/request/disclosure/v2",
    "disclose": [[["pbdf.sidn-pbdf.email.email"]]],
}


@receiver(yivi_session_done)
def yivi_session_done_handler(sender, request, result, yivi_session, **kwargs):
    if not (yivi_session["original_path"] == "/login/" and yivi_session["request"] == yivi_login_request):
        return

    yivi_email = result["disclosed"][0][0]["rawvalue"]
```

### HTML template
In your page HTML template, include the `yivi.js` script (in the head or at the end of the body).

```html
{% load static %}

<script src='{% static "js/yivi.js" %}' type="text/javascript"></script>
```

Include the DOM element where you want the Yivi widget to appear on the page with the id `yivi-web-form`.

```html
<div id="yivi-web-form"></div>
```

And include the following script to initialize the widget as per the [Yivi front-end packages documentation](https://irma.app/docs/irma-frontend/).
Make sure a CSRF token is sent in the request headers and "Accept" and "Content-Type" headers are set to "application/json".
Also, make sure the `Original-Path` header is set to the path of the page where the Yivi session was started.

The following code is an example of how to do this in a Django template.
```html
{{ yivi_request|json_script:"yivi_request" }}
<script>
    const yiviWeb = yivi.newWeb({
        debugging: true,
        element:   '#yivi-web-form',
        session: {
            url: '{% url "yivi_auth:start" %}',
            start: {
                url: o => `${o.url}`,
                method: 'POST',
                headers: {
                    "X-CSRFToken": CSRF_TOKEN,
                    "Accept": 'application/json',
                    "Content-Type": 'application/json',
                    "Original-Path": window.location.pathname,
                },
                body: document.getElementById('yivi_request').textContent,
            },
            result: {
                url: (o, {sessionPtr, sessionToken}) => `{% url "yivi_auth:result" "$sessionToken" %}`.replace('$sessionToken', sessionToken),
                method: 'GET',
                headers: {
                    "X-CSRFToken": CSRF_TOKEN,
                },
            }
      }
    });
    yiviWeb.start().then(() => {
        {% if next_url %}
        window.location.href = '{{ next_url }}';
        {% else %}
        window.location.reload();
        {% endif %}
    });
</script>
```

`yivi_request` is a JSON object containing the request to Yivi.
In the example below, the request is passed from the Django view to the template as a context variable `yivi_request`.
Also, the `next_url` context variable is passed from the Django view to the template to redirect the user after the session.



