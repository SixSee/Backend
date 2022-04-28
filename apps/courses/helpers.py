from .models import Course


def get_latest_courses():
    return Course.objects.filter(is_archived=False, is_live=True).order_by('created_at', 'updated_at').all()
