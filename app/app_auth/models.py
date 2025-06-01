from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Auth Model ::
# class UserDetails(models.Model):
#     id = models.AutoField(primary_key=True)
#     user_name = models.CharField(max_length=50)
#     user_category = models.CharField(max_length=50, default='pending', null=True, blank=True)
#     user_role = models.CharField(max_length=100, default='pending', null=True, blank=True)
#     user_status = models.CharField(max_length=50, default='pending', null=True, blank=True)
#     # FK --
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='details')

#     def __str__(self) -> str:
#         return self.user_name

#     class Meta:
#         db_table = 'auth_user_details'
