from django.db import models


class Posts(models.Model):
	title = models.CharField(max_length=200)
	content = models.TextField()
	author_id = models.IntegerField(db_index=True)
	author_username = models.CharField(max_length=150, blank=True, default="")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.title
