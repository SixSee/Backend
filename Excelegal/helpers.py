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


class GenericDao():
    model = None

    def get_by_id(self, id):
        return self.model.objects.filter(pk=id).first()

    def save_from_dict(self, data_dict, pk=None):
        obj, created = self.model.objects.update_or_create(**data_dict)
        return obj, created