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
    deduct = serializers.BooleanField(allow_null=True, required=False)

    class Meta: 
        model = Exam
        fields = [ 
                "name",
                "teacher",
                "classrooms",
                "password",
                "public",
                "deduct"
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

            if "deduct" in self.validated_data.keys():
                exam.public=self.validated_data["deduct"]

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

    # Updates an already existing exam object
    def update(self, instance, validated_data, exercises=None):
        instance.name = validated_data.get("name", instance.name)
        if exercises:
            exercises_new_pk = []
            exercises_old_pk = []
            exercises_old_marks = []
            try:
                for dict in exercises:
                    obj_mark, in_db = Marks.objects.get_or_create(exam=instance, exercise=Exercise.objects.get(id=dict["exercise"]))
                    print(obj_mark, in_db)
                    if in_db:
                        exercises_new_pk.append(dict["exercise"])
                    else:
                        exercises_old_pk.append(dict["exercise"])
                        exercises_old_marks.append(obj_mark.mark)
                    obj_mark.mark = dict["mark"]
                    obj_mark.save() 
                Marks.objects.filter(exam=instance).exclude(exercise__in=exercises_new_pk+exercises_old_pk).delete()
            except BaseException as e:
                print("cagada")
                Marks.objects.filter(exam=instance, exercise__in=exercises_new_pk).delete()
                for exercise_pk in exercises_old_pk:
                    Marks.objects.get(exam=instance, exercise=exercise_pk).mark = exercises_old_marks[exercises_old_pk.index(exercise_pk)]
                    Marks.objects.get(exam=instance, exercise=exercise_pk).save()
                return JsonResponse({ 'v': False, 'm': "Error updating exercises marks" }, safe=False)

        if "classrooms" in validated_data.keys():
            instance.classrooms.set(validated_data.get("classrooms", instance.classrooms))
        if "public" in self.validated_data.keys():
            instance.public=self.validated_data["public"]
        if "deduct" in self.validated_data.keys():
            instance.deduct=self.validated_data["deduct"]
        if "password" in validated_data.keys():
            instance.password = validated_data.get("password", instance.password)
            instance.save_with_pass()
        else:
            instance.save_no_pass()
        return instance
