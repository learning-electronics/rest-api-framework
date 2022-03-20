from rest_framework import serializers
from account.models import Account
from classroom.models import Classroom

class StudentListing(serializers.RelatedField):
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
    students = StudentListing(allow_null=True, many=True, read_only=True)

    class Meta:
        model = Classroom
        fields = [
                "id",  
                "name",
                "teacher",
                "password",
                "students"
            ]
        extra_kwargs = { 'password': {"write_only":True} }

    def save(self):
        classroom = Classroom(
                    name    = self.validated_data["name"],
                    teacher = self.validated_data["teacher"],
                    password = self.validated_data["password"]
                )
        classroom.save()

        """ if self.is_valid['students']:
            classroom.students.set(self.validated_data["students"])
            classroom.save() """
        
        return classroom

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)