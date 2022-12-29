from rest_framework.views import APIView

from Excelegal.helpers import respond
from .models import Links


class GetLinks(APIView):
    def get(self, request):
        all_links = Links.objects.all()
        response = {x.name: x.hyperlink for x in all_links}
        return respond(200, "Success", response)
