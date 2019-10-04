from django.contrib.auth import get_user_model
from django.contrib import admin
from django.db import models
from django.urls import reverse

User = get_user_model()


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    created = models.DateTimeField('created', auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='books', null=False, blank=False, on_delete=models.CASCADE)
    modified = models.DateTimeField('modified', auto_now=True)

    def get_absolute_url(self):
        return reverse('quotes:detail-book', args=(self.pk,))

    def __str__(self):
        return f"{self.title} by {self.author}"

class Quote(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    text = models.TextField()
    page = models.PositiveIntegerField(blank=True, null=True)
    created = models.DateTimeField('created', auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='quotes', null=False, blank=False, on_delete=models.CASCADE)
    modified = models.DateTimeField('modified', auto_now=True)

    def get_absolute_url(self):
        return reverse('quotes:detail-quote', args=(self.pk,))

    def __str__(self):
        truncated_text = self.text[:20]+'...' if len(self.text) > 20 else self.text
        return f"{truncated_text} by {self.book.author}"

admin.site.register(Book)
admin.site.register(Quote)
