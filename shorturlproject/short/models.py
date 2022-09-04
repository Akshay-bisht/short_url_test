from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

# Create your models here.
from django.contrib.auth.models import AbstractUser

class MyUser(AbstractUser):
    """
    User Model
    """
    mobile_number = models.CharField(max_length=10, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    solution_provider = models.BooleanField(default=False)
    age = models.IntegerField(validators=[MinValueValidator(1)], default=1)
    email = models.EmailField(_('email address'), unique=True)
    otp_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    
class Otp(models.Model):
    """
    opt check model when user forgot the password
    """
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)

    def __str__(self):
        return self.user.username


class UrlDetail(models.Model):
    thread = models.CharField(unique=True, max_length=12)
    website = models.URLField()
