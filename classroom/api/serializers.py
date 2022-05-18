from rest_framework import serializers
from account.models import Account
from classroom.models import Classroom
from exercise.api.serializers import ExerciseSerializer

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
    exercises= ExerciseSerializer(allow_null=True, many=True, read_only=True, required=False)

    class Meta:
        model = Classroom
        fields = [
                "id",  
                "name",
                "teacher",
                "students",
                "exercises",
            ]
            
# Serializers used to create/update classroom objects
class AddClassroomSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Classroom
        fields = [ 
                "name",
                "teacher",
                "password",
                "students",
                "exercises",
            ]
        extra_kwargs = { 'password': {"write_only":True} }

    # Updates an already existing Classroom object
    # It takes a json with optional field "name", "password", "students" and "exercises"
    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        if "students" in validated_data.keys():
            instance.students.set(validated_data.get("students", instance.students))
        if "exercises" in validated_data.keys():
            instance.exercises.set(validated_data.get("exercises", instance.exercises))
        if "password" in validated_data.keys():
            instance.password = validated_data.get("password", instance.password)
            instance.save()
        else:
            instance.save_no_pass()
        return instance
