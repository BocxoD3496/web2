from django.core.management.base import BaseCommand
from study.models import Progress

class Command(BaseCommand):
    help = "Загрузить слова в базу"

    def handle(self, *args, **options):
        words = [
            ("apple", "яблоко"),
            ("dog", "собака"),
            ("cat", "кот"),
            ("house", "дом"),
            ("car", "машина"),
            ("book", "книга"),
            ("sun", "солнце"),
            ("moon", "луна"),
            ("tree", "дерево"),
            ("water", "вода"),
            ("milk", "молоко"),
            ("bread", "хлеб"),
            ("cheese", "сыр"),
            ("school", "школа"),
            ("friend", "друг"),
            ("family", "семья"),
            ("work", "работа"),
            ("computer", "компьютер"),
            ("phone", "телефон"),
            ("music", "музыка"),
            ("movie", "фильм"),
            ("flower", "цветок"),
            ("river", "река"),
            ("mountain", "гора"),
            ("sea", "море"),
            ("food", "еда"),
            ("game", "игра"),
            ("letter", "письмо"),
            ("road", "дорога"),
            ("city", "город"),
        ]

        for en, ru in words:
            Progress.objects.get_or_create(word_en=en, word_ru=ru)

        self.stdout.write(self.style.SUCCESS("✅ Слова загружены в базу"))
