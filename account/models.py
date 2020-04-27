from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

def user_img_upload(instance, filename, *args, **kwargs):
    return f"account/{slugify(instance.username)}_{filename}"

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password, image=None, *args, **kwargs):
        user_obj = self.model(
            username = username,
            email = self.normalize_email(email),
            image = image,
        )
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj
    def create_superuser(self, username, email, password, image=None, *args, **kwargs):
        user_obj = self.create_user(username, email, password,image)
        user_obj.is_admin = True
        user_obj.save(using=self._db)
        return user_obj

class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=120, unique=True)
    email = models.EmailField(max_length=120, unique=True)
    password = models.CharField(max_length=150)
    image = models.ImageField(upload_to=user_img_upload, null=True, blank=True)
    activation_key = models.CharField(max_length=120, null=True, blank=True)
    key_expires = models.DateTimeField(null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


    def __str__(self):
        return self.username

    def is_staff(self, *args, **kwargs):
        return self.is_admin

    def has_module_perms(self, app_label, *args, **kwargs):
        return True
    def has_perm(self, perm, obj=None):
        return True
