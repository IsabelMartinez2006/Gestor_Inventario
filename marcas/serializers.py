from rest_framework import serializers

from .models import Marca


class MarcaSerializer(serializers.ModelSerializer):
    piezas_asociadas = serializers.SerializerMethodField()

    class Meta:
        model = Marca
        fields = ["id_marca", "nombre", "piezas_asociadas"]

    def get_piezas_asociadas(self, marca):
        return marca.total_piezas()

    def validate_nombre(self, valor):
        valor = " ".join(valor.split())
        if not valor:
            raise serializers.ValidationError("Completa el campo para continuar.")
        repetidas = Marca.objects.filter(nombre__iexact=valor)
        if self.instance is not None:
            repetidas = repetidas.exclude(pk=self.instance.pk)
        if repetidas.exists():
            raise serializers.ValidationError("Esa marca ya está registrada.")
        return valor
