from django.db import models
from django.conf import settings

# Create your models here.

class FAQ(models.Model):

    question_en = models.CharField(max_length=300)
    question_hi = models.CharField(max_length=300, blank=True)
    answer_en = models.TextField()
    answer_hi = models.TextField(blank=True)


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_en

class SupportMessage(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    message = models.TextField()

    is_resolved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"