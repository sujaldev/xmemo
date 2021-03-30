from django.db import models


# Create your models here.
class Question(models.Model):
    question = models.TextField()
    date = models.CharField(max_length=17)
    answer = models.TextField()

    def __repr__(self):
        return self.question
