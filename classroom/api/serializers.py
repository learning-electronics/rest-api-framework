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

# Serializer used to pass the classrrom trough the rest api to the front 
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
# Serializers used to create/update classroom objects
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

    # Updates an already existing Classroom object
    # It takes a json with optional field "name" and "password"
    # NOTE: the keyword "students" need to be a list of integers with the id numbers of the students, and should always have 
    # the id's of the students in that class (remove an id if you want to remove a student and keep the other ones)
    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        if "students" in validated_data.keys():
            instance.students.set(validated_data.get("students", instance.students))
        if "password" in validated_data.keys():
            instance.password = validated_data.get("password", instance.password)
            instance.save()
        else:
            instance.save_no_pass()
        return instance