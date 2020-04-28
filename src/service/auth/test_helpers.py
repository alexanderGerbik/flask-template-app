from flask.testing import FlaskClient

from service.auth.token import create_token


class AuthenticatedClient(FlaskClient):
    """
    Test Client which allows to send authenticated requests.
    In order to send authenticated requests,
    set client's attribute 'user' to desired user.
    Set the attribute 'permissions' to desired permissions.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.permissions = ["annotator"]

    def open(self, *args, **kwargs):
        if self.user:
            headers = kwargs.setdefault("headers", {})
            if "Authorization" not in headers:
                token = create_token(
                    self.user,
                    self.permissions,
                )
                token = "Bearer {}".format(token)
                headers["Authorization"] = token
        return super().open(*args, **kwargs)
