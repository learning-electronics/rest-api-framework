from rest_framework import serializers
from exercise.models import Exercise, Theme

class ExerciseSerializer(serializers.ModelSerializer):
    resol = serializers.CharField(allow_null=True, allow_blank=True)

    class Meta:
        model = Exercise
        fields = [
                "teacher",
                "theme",
                "question",
                "ans1",
                "ans2",
                "ans3",
                "correct",
                "unit",
                "resol",
                "date", 
                "img"
            ]

    def save(self):
        exercise = Exercise(
                teacher     = self.validated_data["teacher"],
                question    = self.validated_data["question"],
                ans1        = self.validated_data["ans1"],
                ans2        = self.validated_data["ans2"],
                ans3        = self.validated_data["ans3"],
                correct     = self.validated_data["correct"],
                unit        = self.validated_data["unit"],
                resol       = self.validated_data["resol"]
            )
        
        exercise.save()
        exercise.theme.set(self.validated_data["theme"])
        exercise.save()
        return exercise

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = [  
                "id",
                "name"
            ]
    
    def save(self):
        theme = Theme(
                name    = self.validated_data["name"]
            )
        theme.save()
        return theme
