from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .data import WORDS


class Progress(models.Model):
    word_en = models.CharField(max_length=100, unique=True)
    word_ru = models.CharField(max_length=100)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.word_en} - {self.word_ru}"


@receiver(post_migrate)
def fill_words(sender, **kwargs):
    if sender.name == "study":  # только для нашего приложения
        for en, ru in WORDS:
            Progress.objects.get_or_create(word_en=en, word_ru=ru)
