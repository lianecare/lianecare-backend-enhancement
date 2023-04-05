from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lianecare.courses.models import Module, EnrollmentStatus


@ensure_csrf_cookie
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def changeViewedModuleAjax(request):
    try:
        viewed = request.data['viewed']
        pk = request.data['id_module']
        esito = EnrollmentStatus.objects.filter(pk=pk).update(viewed=viewed)

        return Response({'esito': esito}, status=status.HTTP_200_OK)
    except Module.DoesNotExist:
        return Response({"message": "ID module doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
