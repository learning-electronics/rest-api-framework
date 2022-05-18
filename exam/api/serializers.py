import base64
from rest_framework import serializers
from exam.models import Exam
from account.models import Account
from exercise.api.serializers import ExerciseSerializer
from exercise.models import Exercise

class ExerciseInfo(serializers.RelatedField):
    img = serializers.ImageField(allow_null=True, required=False)
    class Meta:
        model = Exercise
        fields = [
            "id",
            "question",
            "ans1"
            "ans2",
            "ans3",
            "correct",
            "unit",
            "img"
        ]

    def to_representation(self, instance):
        info = {
            "id": instance.id,
            "question": instance.question,
            "ans1": instance.ans1,
            "ans2": instance.ans2,
            "ans3": instance.ans3,
            "correct": instance.correct,
            "unit": instance.unit,
        }
        try:
                info["img"]=instance.img.url
                #info["img"]=base64.b64encode(instance.img.read()) if instance.img != None else None
        except:
                info["img"]=None
        
        return info

# Serializer used to pass the exam trough the rest api to the front with the purpose of the students to see the exam 
class StudentExamSerializer(serializers.ModelSerializer):
    exercises= ExerciseInfo(many=True, read_only=True)
    class Meta:
        model = Exam
        fields = [
            "id",
            "name",
            "exercises",
        ]

# Serializers used to create/update exam objects
class AddExamSerializer(serializers.ModelSerializer):
    public = serializers.BooleanField(allow_null=True, required=False)

    class Meta: 
        model = Exam
        fields = [ 
                "name",
                "teacher",
                "exercises",
                "classrooms",
                "marks",
                "password",
                "public"
            ]
        extra_kwargs = { 'password': {"write_only":True} }

    # Updates an already existing exam object
    # It takes a json with optional field "name", "marks", "exercises", "classrooms" and "password"
    def update(self, instance, validated_data):
        print("UPDATE")
        instance.name = validated_data.get("name", instance.name)
        instance.marks = validated_data.get("marks", instance.marks)
        if "exercises" in validated_data.keys():
            instance.exercises.set(validated_data.get("exercises", instance.exercises))
        if "classrooms" in validated_data.keys():
            instance.students.set(validated_data.get("classrooms", instance.students))
        if "public" in self.validated_data.keys():
            instance.public=self.validated_data["public"]
        if "password" in validated_data.keys():
            instance.password = validated_data.get("password", instance.password)
            instance.save()
        else:
            instance.save_no_pass()
        return instance

    def save(self):
        exam = Exam(
                name    = self.validated_data["name"],
                teacher = self.validated_data["teacher"],
                marks   = self.validated_data["marks"],
            )

        if "password" in self.validated_data.keys():
            exam.password=self.validated_data["password"]

        if "public" in self.validated_data.keys():
            exam.public=self.validated_data["public"]

        exam.save_with_pass()
        if "classrooms" in self.validated_data.keys():
            exam.classrooms.set(self.validated_data["classrooms"])
        exam.exercises.set(self.validated_data["exercises"])
        exam.save_no_pass()
        return exam