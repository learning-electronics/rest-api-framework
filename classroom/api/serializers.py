from rest_framework import serializers
from account.models import Account
from classroom.models import Classroom
from django.contrib.auth.hashers import make_password

class AccountInfo(serializers.RelatedField):
    class Meta:
        model = Account
        fields = [
                    "id",
                    "first_name",
                    "last_name",        
            ]

    def to_representation(self, instance):
        return "%d : %s %s" % (instance.id, instance.first_name, instance.last_name)


class ClassroomSerializer(serializers.ModelSerializer):
    students = AccountInfo(allow_null=True, many=True, read_only=True, required=False)
    teacher  = AccountInfo(allow_null=True, read_only=True)

    class Meta:
        model = Classroom
        fields = [
                "id",  
                "name",
                "teacher",
                "students"
            ]

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class AddClassroomSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Classroom
        fields = [ 
                "name",
                "teacher",
                "password",
                "students"
            ]
        extra_kwargs = { 'password': {"write_only":True} }

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.students.set(validated_data.get("students", instance.students))
        if "password" in validated_data.keys():
            instance.password = validated_data.get("password", instance.password)
            instance.save()
        else:
            instance.save_no_pass()
        return instance