from rest_framework import serializers
from app.models import Scheme

class SchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme
        fields = ('id',
                  'razaoSocial',
                  'nomeMunicipio',
                  'nfCode',
                  'dataEmissao',
                  'CNPJ',
                  'valorNota',
                  'ISS',
                  'featureDesc')
