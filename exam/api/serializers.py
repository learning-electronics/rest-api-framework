from classroom.models import Classroom
from rest_framework import serializers
from exam.models import Exam, Marks, SubmittedExam
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

# Serializer used to plass the exam trough the rest api to the front with the purpose of the professor to see the exam info
class ProfessorExamSerializer(serializers.ModelSerializer):
    exercises= ExerciseInfo(many=True, read_only=True)
    class Meta:
        model = Exam
        fields = [
            "name",
            "public",
            "deduct",
            "date_created",
            "exercises",
            "timer",
            "repeat",
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
            "timer",
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

# Serializers used to create SubmittedExam objects
class AddSubmittedExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmittedExam
        fields = [
            "submitted_exam",
            "exam_classroom",
            "student",
            "answers",
            "final_mark",
        ]

    def save(self):
        submitted_exam = SubmittedExam(
                submitted_exam = self.validated_data["submitted_exam"],
                exam_classroom = self.validated_data["exam_classroom"],
                student = self.validated_data["student"],
                answers = self.validated_data["answers"],
                final_mark = self.validated_data["final_mark"],
            )
        submitted_exam.save()
        return submitted_exam

    def validate(self, data):
        if len(data["answers"].keys()) != Marks.objects.filter(exam=data["submitted_exam"]).count():   
            raise serializers.ValidationError("The number of answers is not the same as the number of exercises")
        for key in data["answers"].keys():
            if not Exercise.objects.filter(id=key).exists():
                raise serializers.ValidationError("The exercise with id {} does not exist".format(key))
            if not Marks.objects.filter(exam=data["submitted_exam"], exercise__id=key).exists():
                raise serializers.ValidationError("The exercise with id {} is not in the exam".format(key))
        return data

# Serializers used to create/update exam objects
class AddExamSerializer(serializers.ModelSerializer):
    password = serializers.CharField(allow_null=True, required=False)
    public   = serializers.BooleanField(allow_null=True, required=False) 
    deduct   = serializers.DecimalField(allow_null=True, required=False, max_digits=4, decimal_places=2)
    timer    = serializers.CharField(max_length=5, allow_null=True, required=False)
    repeat   = serializers.BooleanField(allow_null=True, required=False) 
    class Meta: 
        model = Exam
        fields = [ 
                "name",
                "teacher",
                "classrooms",
                "password",
                "public",
                "deduct",
                "timer",
                "repeat",
            ]
        extra_kwargs = { 'password': {"write_only":True} }

    def save(self, exercises):
            exam = Exam(
                    name    = self.validated_data["name"],
                    teacher = self.validated_data["teacher"],
                )

            if "public" in self.validated_data.keys():
                exam.public=self.validated_data["public"]

            if "deduct" in self.validated_data.keys():
                exam.deduct=self.validated_data["deduct"]

            if "timer" in self.validated_data.keys():
                exam.timer=self.validated_data["timer"]

            if "repeat" in self.validated_data.keys():
                exam.repeat=self.validated_data["repeat"]

            if "password" in self.validated_data:
                exam.password = self.validated_data["password"]
                exam.save_with_pass()
            else:
                exam.save_no_pass()

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
                    if in_db:
                        exercises_new_pk.append(dict["exercise"])
                    else:
                        exercises_old_pk.append(dict["exercise"])
                        exercises_old_marks.append(obj_mark.mark)
                    obj_mark.mark = dict["mark"]
                    obj_mark.save() 
                Marks.objects.filter(exam=instance).exclude(exercise__in=exercises_new_pk+exercises_old_pk).delete()
            except BaseException as e:
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
        if "timer" in self.validated_data.keys():
            instance.timer=self.validated_data["timer"]    
        if "repeat" in self.validated_data.keys():
            instance.repeat=self.validated_data["repeat"]
        if "password" in validated_data.keys():
            if self.validated_data["password"] == None:
                instance.password = None
                instance.save_no_pass()
            else:
                instance.password = validated_data.get("password", instance.password)
                instance.save_with_pass()
        else:
            instance.save_no_pass()
        return instance
