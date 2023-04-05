from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .permissions import IsOwnerOrReadOnly, IsOwnerCaregiverOrReadOnly
from .serializers import CaregiverProMoreSerializer, ServiceSerializer, SubCategorySerializer, JobPostSerializer
from ..models import Service, Category, CaregiverProMore, JobPost

from ..templatetags.caregiver_tags import skill_list, availability_grid, subCategoriesList, servicesList
from ..enums import JobPostStatus


class CaregiverProDetailAPIView(RetrieveUpdateAPIView):
    serializer_class = CaregiverProMoreSerializer
    queryset = CaregiverProMore.objects.all()
    lookup_field = "user__username"
    lookup_url_kwarg = "username"
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


@ensure_csrf_cookie
@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsOwnerOrReadOnly])
def skillUpdateFragmentAjax(request):
    if request.method == 'PATCH':
        try:
            caregiver = CaregiverProMore.objects.get(user=request.user)
        except CaregiverProMore.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CaregiverProMoreSerializer(caregiver, data=request.data, partial=True)
        time_flag = True if request.data['time'] == 'true' else False
        if serializer.is_valid():
            serializer.save()
            if time_flag:
                html_table_time = availability_grid(caregiver.availability)
                return Response({"message": "Disponibilità aggiornate", "data": html_table_time},
                                status=status.HTTP_200_OK)
            else:
                html_list = skill_list(caregiver)
                return Response({"message": "Dati aggiornati", "data": html_list, "caregiver": serializer.data},
                                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Services.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, IsOwnerCaregiverOrReadOnly]

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(caregiver=self.request.user)


@ensure_csrf_cookie
@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsOwnerCaregiverOrReadOnly])
def serviceUpdateView(request):
    caregiver = request.user
    try:
        service = Service.objects.get(pk=request.data['id'], caregiver=caregiver)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        service.delete()
        services = Service.objects.filter(caregiver=caregiver)
        html_list = servicesList(services)
        return Response({"data": html_list}, status=status.HTTP_200_OK)

    if request.method == 'PATCH':
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            services = Service.objects.filter(caregiver=caregiver)
            html_list = servicesList(services)
            return Response({"data": html_list}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@ensure_csrf_cookie
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def jobPostUpdateView(request):
    user = request.user
    try:
        job_post = JobPost.objects.get(pk=request.data['id'], user=user)
    except JobPost.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = JobPostSerializer(job_post, data=request.data, partial=True)
    if serializer.is_valid():
        if serializer.validated_data.get('is_active') in [0, 1]:
            is_active = serializer.validated_data.get('is_active')
            new_status = JobPostStatus.ACTIVE if is_active == True else JobPostStatus.NO_SHOW
        elif serializer.validated_data.get('status'):
            new_status = serializer.validated_data.get('status')
            is_active = True if serializer.validated_data['status'] == 'ACTIVE' else False
        serializer.save(status=new_status, is_active=is_active)
        return Response({"msg": 'Job Post aggiornato'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobPostUpdate(generics.UpdateAPIView):
    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_update(self, serializer):
        serializer.status = JobPostStatus.ACTIVE if serializer.is_active == True else JobPostStatus.NO_SHOW
        serializer.save()


@ensure_csrf_cookie
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getSubcategoriesAjax(request):
    try:
        category = Category.objects.get(pk=request.data['id_category'], active=True)
        subcategories = category.subcategories.all()
        forJobPost = True if request.data['forJobPost'] == True else False
        get_edit_service_id = request.data.get('service_id', None)
        if subcategories:
            serializer = SubCategorySerializer(subcategories, many=True)
            if get_edit_service_id:
                obj = Service.objects.get(pk=get_edit_service_id)
                get_selected_sub_category = [ data.id for data in obj.subcategories.all()]
                list_html = subCategoriesList(subcategories, None, get_selected_sub_category)
                service_other_detail= {
                    'year_of_exp': obj.experience,
                    'price': obj.price,
                    'has_references': obj.has_references,
                    'max_distance': obj.max_distance,
                    'note': obj.note,
                }
                return Response({'data': serializer.data, 'list_html': list_html, 'service_other_detail': service_other_detail}, status=status.HTTP_200_OK)
            else:
                list_html = subCategoriesList(subcategories, forJobPost)
                return Response({'data': serializer.data, 'list_html': list_html}, status=status.HTTP_200_OK)
    except Category.DoesNotExist:
        return Response({"message": "Errore categoria"}, status=status.HTTP_400_BAD_REQUEST)
