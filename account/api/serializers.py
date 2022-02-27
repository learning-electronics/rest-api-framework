from tkinter import Image
from rest_framework import serializers

from account.models import Account

class RegistrationSerialiazer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source='image.file', allow_null=True)

    class Meta:
        model = Account
        fields = [  
                "email",
                "first_name",
                "last_name",
                "birth_date",
                "password",
                "avatar"
            ]
        extra_kwargs = { 'password': {"write_only":True} }

    def save(self):
        i = None

        if self.instance is not None :
            if self.instance.avatar:
                self.instance.avatar.delete()
            
            image = Image.objects.get(user=self.instance)
            image.file = self.validated_data.get('image')['file']
            i = image.file

        account = Account(
                    email = self.validated_data["email"],
                    first_name = self.validated_data["first_name"],
                    last_name = self.validated_data["last_name"],
                    birth_date = self.validated_data["birth_date"],
                    avatar = i
                )
        
        password = self.validated_data['password']
        account.set_password(password)
        account.save()
        return account

    def save_with_img(self):
        if self.instance.avatar:
            self.instance.avatar.delete()
        
        image = Image.objects.get(user=self.instance)
        image.file = self.validated_data.get('image')['file']
        self.save()
