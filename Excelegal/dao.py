from apps.blogs.dao import BlogsDao, BlogReviewDao
from apps.bulletin.dao import BulletinDao
from apps.courses.dao import CourseDao, TopicDao, CourseReviewDao
from apps.classes.dao import ScheduleClassDao
from apps.internship.dao import InternshipDao

class DaoCollection():
    course_dao = CourseDao()
    topic_dao = TopicDao()
    course_review_dao = CourseReviewDao()
    blogs_dao = BlogsDao()
    blogs_review_dao = BlogReviewDao()
    bulletin_dao = BulletinDao()
    schedule_class_dao = ScheduleClassDao()
    internship_dao = InternshipDao()

    def get_by_ids(self, model, ids):
        return (
            model.objects.filter(id__in=ids)
        )


dao_handler = DaoCollection()
