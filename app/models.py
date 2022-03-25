from django.db import models

defaultEmissao = {"coordinates": "((0, 0), (0, 0))",
            "OPTIONS": "-l por --psm 6"}
class Scheme(models.Model):

    nomeMunicipio = models.CharField(max_length=90, default='Desconhecido')
    nfCode = models.JSONField(name='nfCode')
    dataEmissao = models.JSONField(name='dataEmissao')
    CNPJ = models.JSONField(name='CNPJ')
    valorNota = models.JSONField(name='valorNota')
    ISS = models.JSONField(name='ISS')
    razaoSocial = models.JSONField(name='razaoSocial')

