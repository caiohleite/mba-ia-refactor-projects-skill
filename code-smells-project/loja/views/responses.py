from flask import jsonify


def json_response(result):
    payload, status_code = result
    return jsonify(payload), status_code
