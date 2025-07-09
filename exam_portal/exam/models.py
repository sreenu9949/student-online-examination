from django.db import models

# Create your models here.
from django.db import models

class Questions(models.Model):  # Note: Capitalize class name by convention
    question_text = models.CharField(max_length=255)
    option_a = models.CharField(max_length=100)
    option_b = models.CharField(max_length=100)
    option_c = models.CharField(max_length=100)
    option_d = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)  # Remove `unique=True` if not needed

    def __str__(self):
        return self.question_text
