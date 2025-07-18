from django.db import models

class QuestionType(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Наименование типа")
    description = models.TextField(verbose_name="Описание типа")

    class Meta:
        verbose_name = 'Тип вопроса'
        verbose_name_plural = 'Типы вопросов'

    def __str__(self):
        return self.name


class FAQ(models.Model):
    question = models.CharField(max_length=255, unique=True, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    type = models.ForeignKey(QuestionType, on_delete=models.CASCADE, related_name="faqs")

    class Meta:
        verbose_name = 'Вопрос и ответ'
        verbose_name_plural = 'Вопросы и ответы'

    def __str__(self):
        return self.question