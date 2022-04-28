from Excelegal.helpers import GenericDao
from .models import Bulletin


class BulletinDao(GenericDao):
    model = Bulletin

    def get_by_category(self, category):
        return self.model.objects.filter(category=category).all()
