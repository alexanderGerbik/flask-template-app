from flask import jsonify

from . import bp


@bp.route("/login", methods=["POST"])
def login():
    token = ''
    return jsonify(token=token)
