from Excelegal.helpers import GenericDao
from .models import Course, Topic


class CourseDao(GenericDao):
    model = Course


class TopicDao(GenericDao):
    model = Topic
