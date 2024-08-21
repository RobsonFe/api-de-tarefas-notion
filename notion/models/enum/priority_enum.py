from django.db import models


class PriorityEnum(models.TextChoices):
    ATENCAO = 'Atenção'
    BAIXA = 'Baixa'
    ALTA = 'Alta'
