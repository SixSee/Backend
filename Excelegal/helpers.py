from rest_framework.response import Response


def respond(status, message="", payload=False):
    response_json = {}
    if message:
        response_json['message'] = message
    if payload:
        response_json['payload'] = payload

    if bool(response_json) is False:
        raise Exception("Either message or payload is required")

    return Response(response_json, status=status)