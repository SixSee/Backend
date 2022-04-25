from Excelegal.helpers import GenericDao
from .models import Course, Topic, CourseReview


class CourseDao(GenericDao):
    model = Course

    def create_course(self, title, description, owner, is_archived=False):
        course = self.model(title=title, description=description, owner=owner, is_archived=is_archived)
        course.save()
        return course

    def get_by_slug(self, slug):
        return self.model.objects.filter(slug=slug).first()


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


class CourseReviewDao(GenericDao):
    model = CourseReview

    def create_review(self, course, review_by, text, rating):
        review = self.model(course=course, review_by=review_by, text=text, rating=rating)
        review.save()
        return review
