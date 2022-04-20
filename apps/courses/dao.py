from Excelegal.helpers import GenericDao
from .models import Course, Topic


class CourseDao(GenericDao):
    model = Course

    def create_course(self, title, description, owner):
        course = self.model(title=title, description=description, owner=owner)
        course.save()
        return course


class TopicDao(GenericDao):
    model = Topic

    def create_topic(self, title, text, index, course):
        course = self.model(title=title, text=text, course=course, index=index)
        course.save()
        return course

    def shift_topics_down(self, index, course):
        topics = self.model.objects.filter(course=course, index__gte=index).order_by('index').all()
        for topic in topics:
            topic.index = index + 1
            index += 1
            topic.save()
