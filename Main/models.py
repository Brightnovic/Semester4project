from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import AbstractUser
from   django.conf import  settings
from django.utils.timezone import now
from datetime import timedelta
from dateutil.relativedelta import relativedelta  
from django.core.exceptions import ValidationError
 

 









# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, full_name=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        
        user = self.model(email=email, username=username, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,  email, username, password=None):
        user = self.create_user(
            email, username, password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user



# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, blank=True, null=True, default="User")
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True, default="profile_photos/default.jpg")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

     
    @property
    def is_trainer(self):
        return Trainer.objects.filter(user=self).exists()


    def __str__(self):
        return self.username
    
    def has_module_perms(self, app_label):
        return self.is_admin

# Category model
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


# PackageType model
class PackageType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


# Package model
class Package(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    package_type = models.ForeignKey(PackageType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    trainer = models.ForeignKey('Trainer', on_delete=models.CASCADE, related_name='packages', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField()      
    description = models.TextField()
    available = models.BooleanField(default=True)
    
    # to see how many people who booked this package
    @property
    def bookings_count(self):
        return self.booking_set.count()


    def __str__(self):
        return f"{self.name} - {self.category.name}"



# Trainer Model
class Trainer(models.Model):
    EXPERTISE_CHOICES = [
        ('general_fitness', 'General Fitness'),
        ('yoga', 'Yoga'),
        ('strength_training', 'Strength Training'),
        ('cardio', 'Cardio'),
        ('nutrition', 'Nutrition'),
        ('pilates', 'Pilates'),
        ('crossfit', 'CrossFit'),
        ('bodybuilding', 'Bodybuilding'),
        ('martial_arts', 'Martial Arts'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name="trainer")

    expertise = models.CharField(max_length=50, choices=EXPERTISE_CHOICES, default='general_fitness')
    bio = models.TextField()
    instagram_handle = models.CharField(max_length=255, blank=True, null=True)
    facebook_handle = models.CharField(max_length=255, blank=True, null=True)
    linkedin_handle = models.CharField(max_length=255, blank=True, null=True)
    X_handle = models.CharField(max_length=255, blank=True, null=True)



    # New fields for availability
    available_days = models.JSONField(default=list)  # Example: ["Monday", "Wednesday", "Friday"]
    max_bookings_per_day = models.PositiveIntegerField(default=5)
    def __str__(self):
        return self.user.username


# Product model (e.g., for gym merchandise)
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField(upload_to='products/', blank=True, null=True)  # Product photo
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name



class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(default=now)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)  # Auto-calculated later
    status = models.CharField(
        max_length=50, 
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], 
        default='pending'
    )
    payment_status = models.CharField(
        max_length=50, 
        choices=[('pending', 'Pending'), ('paid', 'Paid')], 
        default='pending'
    )

    def clean(self):
        """Prevent duplicate bookings and ensure a booking cannot be confirmed without payment."""
        
        # Prevent duplicate booking
        if not self.pk and Booking.objects.filter(user=self.user, package=self.package).exists():
            raise ValidationError("You have already booked this package.")

        # Prevent confirmation if payment is not made
        if self.status == "confirmed" and self.payment_status != "paid":
            raise ValidationError("Booking cannot be confirmed without payment.")

    def save(self, *args, **kwargs):
        """Auto-calculate end_date and prevent overbooking."""
        
        # Auto-set end_date
        if self.start_date and self.package:
            self.end_date = self.start_date + relativedelta(months=self.package.duration)

            # Prevent overbooking
            if self.package.trainer:
                bookings_on_day = Booking.objects.filter(
                    package__trainer=self.package.trainer,
                    start_date__date=self.start_date.date()
                ).count()

                if bookings_on_day >= self.package.trainer.max_bookings_per_day:
                    raise ValidationError("This trainer is fully booked on this date.")

        super().save(*args, **kwargs)


    def __str__(self):
        return f"Booking by {self.user.username} for {self.package.name}"

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    currency = models.CharField(max_length=10, default='NGN')

    payment_method = models.CharField(
        max_length=50,
        choices=[('Paystack', 'Paystack')],
        default='Paystack'
    )

    status = models.CharField(
        max_length=50,
        choices=[('completed', 'Completed'), ('pending', 'Pending'), ('failed', 'Failed')],
        default='pending'
    )

    def __str__(self):
        if self.booking:
            return f"Payment for booking by {self.user.username} - {self.booking.package.name}"
        elif self.product:
            return f"Payment for product {self.product.name} by {self.user.username}"
        else:
            return f"Payment by {self.user.username}"



class Appointment(models.Model):
    Complete_name = models.CharField(max_length=255)
    subject = models.CharField(max_length=500)
    email = models.EmailField(unique=False)
    question_message = models.CharField(max_length=1000)
    mobile_number = models.CharField(max_length=20)
    def __str__(self):
        if self.Complete_name:
            return f"New Appointment by {self.Complete_name } "
        else:
            return f"Error in Appointment booking"