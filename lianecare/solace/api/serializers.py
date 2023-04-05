from rest_framework import serializers

from lianecare.solace.models import FamilyMember, Service, Category, SubCategory, CaregiverProMore, JobPost


class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = '__all__'


class CaregiverProMoreSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(trim_whitespace=False)

    class Meta:
        model = CaregiverProMore
        exclude = ['id', 'user', 'how_know_us', 'created', 'modified']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class JobPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPost
        fields = '__all__'
