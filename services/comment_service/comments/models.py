from django.db import models


class Comments(models.Model):
	post_id = models.IntegerField(db_index=True)
	author_id = models.IntegerField(db_index=True)
	author_username = models.CharField(max_length=150, blank=True, default="")
	body = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Comment {self.id}"
