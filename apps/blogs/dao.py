from Excelegal.helpers import GenericDao
from .models import Blog


class BlogsDao(GenericDao):
    model = Blog

    def get_by_type(self, blog_type, order='created_at', is_live=True, is_archived=False):
        return (self.model.objects.filter(type=blog_type,
                                          is_live=is_live,
                                          is_archived=is_archived).order_by(order).all())

    def get_by_slug(self, slug):
        return self.model.objects.filter(slug=slug).first()
