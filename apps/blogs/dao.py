from Excelegal.helpers import GenericDao
from .models import Blog, BlogReview


class BlogsDao(GenericDao):
    model = Blog

    def get_by_type(self, blog_type, order='created_at', is_live=True, is_archived=False):
        return (self.model.objects.filter(type=blog_type,
                                          is_live=is_live,
                                          is_archived=is_archived).order_by(order).all())

    def get_by_slug(self, slug):
        return self.model.objects.filter(slug=slug).first()


class BlogReviewDao(GenericDao):
    model = BlogReview

    def create_review(self, blog, review_by, text, rating):
        review = self.model(blog=blog, review_by=review_by, text=text, rating=rating)
        review.save()
        return review
