from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Marca
from .serializers import MarcaSerializer


class MarcaViewSet(viewsets.ModelViewSet):
    """CRUD de marcas en JSON.(lectura con sesión, escritura solo admin)."""

    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer

    def destroy(self, request, *args, **kwargs):
        marca = self.get_object()
        if marca.total_piezas():
            return Response(
                {"detalle": "No se puede eliminar: la marca tiene piezas asociadas."},
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)
