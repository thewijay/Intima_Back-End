from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None  # Disable username field

    # Additional fields collected after login
    first_name = models.CharField(max_length=30, blank=True, verbose_name="First Name")
    last_name = models.CharField(max_length=30, blank=True, verbose_name="Last Name")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Date of Birth")

    gender = models.CharField(
        max_length=30,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('trans_male', 'Transgender Male'),
            ('trans_female', 'Transgender Female'),
            ('non_binary', 'Non-Binary / Non-Conforming'),
            ('other', 'Other'),
        ],
        blank=True,
        verbose_name="Gender Identity"
    )
    gender_other = models.CharField(max_length=50, blank=True, null=True)

    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    marital_status = models.CharField(max_length=20, choices=[('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced')], blank=True, verbose_name="Marital Status")
    sexually_active = models.BooleanField(null=True, blank=True, verbose_name="Are you sexually active?")
    menstrual_cycle = models.TextField(null=True, blank=True, verbose_name="Menstrual Cycle Details")
    medical_conditions = models.TextField(null=True, blank=True, verbose_name="Medical Conditions")

    profile_completed = models.BooleanField(default=False)


    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
