from django.db import models


class StatusEnum(models.TextChoices):
    NAO_INICIADA = 'Não iniciada'
    EM_ANDAMENTO = 'Em andamento'
    CONCLUIDO = 'Concluído'
