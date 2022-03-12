from rest_framework import serializers
from exercise.models import Exercise

class ExerciseSerializer(serializers.ModelSerializer):
    #img = serializers.ImageField(source='image.file', allow_null=True)
    #resol = serializers.CharField(allow_null=True)

    class Meta:
        model = Exercise
        fields = [  
                "teacher",
                "theme",
                "question",
                #"img",
                "ans1",
                "ans2",
                "ans3",
                "correct",
                "unit",
                #"resol"
            ]

    def save(self):
        exercise = Exercise(
                teacher  = self.validated_data["teacher"],
                #theme    = self.validated_data["theme"],
                question    = self.validated_data["question"],
                #img         = self.validated_data["img"],
                ans1        = self.validated_data["ans1"],
                ans2        = self.validated_data["ans2"],
                ans3        = self.validated_data["ans3"],
                correct     = self.validated_data["correct"],
                unit        = self.validated_data["unit"],
                #resol       = self.validated_data["resol"]
            )

        exercise.theme.set(self.validated_data["theme"])
        exercise.save()
        return exercise
