from django.db import models


class Marca(models.Model):
    id_marca = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "marcas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def total_piezas(self):
       
        relacion = getattr(self, "piezas", None)
        return relacion.count() if relacion is not None else 0
