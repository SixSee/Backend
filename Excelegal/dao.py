from apps.courses.dao import CourseDao, TopicDao


class DaoCollection():
    course_dao = CourseDao()
    topic_dao = TopicDao()

    def get_by_ids(self, model, ids):
        return (
            model.objects.filter(id__in=ids)
        )


dao_handler = DaoCollection()
