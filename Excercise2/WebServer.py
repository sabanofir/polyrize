from uuid import uuid4

import jwt
from jwt.exceptions import DecodeError
from sanic import Sanic
from sanic import response

app = Sanic()

# Default credentials
DEFAULT_USERNAME = "username"
DEFAULT_PASSOWRD = "password"
COOKIE_NAME = "auth"
# Just for this text, in production we should choose static and unique secret
SECRET = uuid4().hex


def encode_data(data):
    return jwt.encode(data, SECRET, algorithm='HS256').decode()


def decode_data(data):
    return jwt.decode(data.encode(), SECRET, algorithm='HS256')


def logged_in_only(func):
    def wrap(request, *args, **kwargs):
        # Check if authorized
        cookies = request.cookies
        # If cookie doesn't present return error
        if COOKIE_NAME not in cookies:
            return response.json({"status": "error"}, status=403)
        # If unable to parse cookie (bad cookie), return error
        try:
            decoded_cookie = decode_data(cookies.get(COOKIE_NAME))
        except DecodeError:
            return response.json({"status": "error"}, status=403)

        if "user" in decoded_cookie and decoded_cookie["user"] == DEFAULT_USERNAME:
            return func(request, *args, **kwargs)
        # If data is malformed or user is not privileged to access, return error code
        return response.json({"status": "error"}, status=403)
    wrap.__name__ = func.__name__
    return wrap


@app.route("/login", methods=["POST"])
async def login(request):
    # a=1&b=2
    post_params = {param.split("=")[0]: param.split("=")[1] for param in [p for p in request.body.decode().split("&")] if "=" in param}
    username = post_params.get("username", "")
    password = post_params.get("password", "")
    if username == DEFAULT_USERNAME and password == DEFAULT_PASSOWRD:
        auth_token = encode_data({"user": username})
        return response.json({"status": "ok"}, headers={"Cookie": f"{COOKIE_NAME}={auth_token}"})
    else:
        return response.json({"status": "error"}, status=401)


@app.route("/simplify", methods=["POST"])
@logged_in_only
async def simplify(request):
    return response.json({obj["name"]: obj[[key for key in obj.keys() if "val" in key.lower()][0]] for obj in request.json})


@app.route("/", methods=["GET"])
async def index(request):
    return response.text("Please login to use the simplifier")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
