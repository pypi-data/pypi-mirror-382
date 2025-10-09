from hyperflask import current_app, request, abort
import functools
import requests


def validate_captcha():
    secret = current_app.config.get("RECAPTCHA_SECRET_KEY")
    if not secret:
        raise Exception("You must set RECAPTCHA_SECRET_KEY in your app config to use reCAPTCHA.")
    response = request.form["recaptcha_token"]
    r = requests.post("https://www.google.com/recaptcha/api/siteverify", params={"secret": secret, "response": response})
    if r.status_code == 200:
        data = r.json()
        return data["success"]
    return False


def validate_captcha_when_configured(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if current_app.config.get("RECAPTCHA_SITE_KEY"):
            if not validate_captcha():
                abort(400)
        return func(*args, **kwargs)
    return wrapper
