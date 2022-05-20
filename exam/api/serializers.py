import base64
from rest_framework import serializers
from exam.models import Exam, Marks
from exercise.models import Exercise
from django.http.response import JsonResponse

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
            "img",
        ]

    def to_representation(self, instance):
        info = {
            "id": instance.id,
            "question": instance.question,
            "ans1": instance.ans1,
            "ans2": instance.ans2,
            "ans3": instance.ans3,
            "correct": instance.correct,
            "unit": instance.unit 
        }
        try:
            info["img"]=instance.img.url
        except:
            info["img"]=None
        
        return info

class MarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Marks
        fields = [
            "exercise",
            "mark"
        ]

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

"""    # Updates an already existing exam object
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
                password= self.validated_data["password"]
            )

        if "public" in self.validated_data.keys():
            exam.public=self.validated_data["public"]

        print("1")
        exam.save_with_pass()
        print("2")
        if "classrooms" in self.validated_data.keys():
            exam.classrooms.set(self.validated_data["classrooms"])
        print("2.5")
        print(self.validated_data)
        print("2.6")
        exam.exercises.set(self.validated_data["exercises"])
        print("3")
        exam.save_no_pass()
        print("4")
        return exam """

#Serializers used to create/update relation between an exam and an exercise
class AddMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marks
        fields = [
            "exam",
            "exercise",
            "mark"
        ]

    def save(self):
        mark = Marks(
                exam = self.validated_data["exam"],
                exercise = self.validated_data["exercise"],
                mark = self.validated_data["mark"]
            )
        mark.save()
        return mark

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
                "password",
                "public"
            ]
        extra_kwargs = { 'password': {"write_only":True} }

    def save(self, exercises):
            exam = Exam(
                    name    = self.validated_data["name"],
                    teacher = self.validated_data["teacher"],
                    password= self.validated_data["password"]
                )

            if "public" in self.validated_data.keys():
                exam.public=self.validated_data["public"]

            exam.save_with_pass()
            if "classrooms" in self.validated_data.keys():
                exam.classrooms.set(self.validated_data["classrooms"])

            for dict in exercises:
                dict["exam"]=exam.id
                newMark = AddMarkSerializer(data=dict)
                if newMark.is_valid():
                    newMark.save()
                else:
                    exam.delete()
                    return JsonResponse({ 'v': False, 'm': newMark.errors }, safe=False)
            exam.save_no_pass()
            return exam
