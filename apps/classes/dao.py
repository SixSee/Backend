from Excelegal.helpers import GenericDao
from .models import ScheduleClass


class ScheduleClassDao(GenericDao):
    model = ScheduleClass

    def get_by_slug(self, slug):
        return self.model.objects.filter(slug=slug).first()
