from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from .models import Booking, Trainer , Package
from django.contrib.auth.decorators import login_required
from .models import CustomUser , Appointment , Booking, Payment
from .forms import ProfileUpdateForm , UpdateTrainerInfo, TrainerAvailabilityForm , ContactForm
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import uuid
from Main.utils.paystack import verify_paystack_payment

from django.conf import settings
 
from django.http import JsonResponse
import json
import requests
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

#Appointment
def appointment(request):
    if request.method == 'POST':
        Complete_name = request.POST.get('Complete_name')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')
        subject = request.POST.get('subject')
        question_message = request.POST.get('question_message')

        Appointment.objects.create(
            Complete_name=Complete_name,
            email=email,
            mobile_number=mobile_number,
            subject=subject,
            question_message=question_message
        )
        messages.success(request, "submitted")

        return redirect('home')
    return render(request, 'home.html')

def features_benefit(request):

    return render(request, 'Main/features-and-benefits.html')
 
def services(request):

    return render(request, 'Main/services.html')



def render_pdf_view(request, template_name):
    template = get_template(template_name)
    html = template.render({})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="payment_status.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response

# Login and Registration View
def auth_view(request):
    User = get_user_model()
     
    if request.method == 'POST':
        # Handle Login
        if 'login' in request.POST:
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            user = User.objects.filter(email=email).first()
            if user:
              
                if user.check_password(password):
                    login(request, user)
                    messages.success(request, "Login successful")
                    return redirect('home')
                else:
                    messages.error(request, "Incorrect Details Provided")
                     
            else:
                 
                messages.error(request, "User not Found")
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect('auth')

        # Handle Registration
        elif 'register' in request.POST:
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')

             
            
            if not email or not username or not password:
                print(email, username, password)
                messages.error(request, "All fields are required.")
                return redirect('auth')

            if User.objects.filter(email=email).exists():
                 
                messages.error(request, "Email already registered.")
                return redirect('auth')

            if User.objects.filter(username=username).exists():
                 
                messages.error(request, "Username already taken.")
                return redirect('auth')

            try:
                user = User.objects.create_user(
                    email=email, username=username, password=password
                )
                 
                messages.success(request, "Account created successfully! Please login.")
                return redirect('auth')
            except Exception as e:
                 
                messages.error(request, f"Error: {str(e)}")
                return redirect('auth')
    return render(request, 'Main/login.html')


def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')


@login_required
def profile(request):
    if not request.user.is_authenticated:
        
        messages.success(request, "You Must  Login First")
        return redirect('auth')
    
     
    form = ProfileUpdateForm(instance=request.user)
    return render(request, 'Main/profile.html', {'form': form})


@login_required
def profile2(request):
    """Allow trainers to see bookings for their packages."""
    if not hasattr(request.user, 'trainer') or request.user.trainer is None:
        return redirect('profile')  # Redirects only non-trainers

    trainer_packages = Package.objects.filter(trainer=request.user.trainer)  # Use `request.user.trainer`
    bookings = Booking.objects.filter(package__in=trainer_packages).order_by('-booking_date')

    return render(request, 'Main/profile2.html', {'bookings': bookings})




def about_us(request):
    trainers = Trainer.objects.all()
    packages = Package.objects.all()
    return render(request, 'Main/about.html', {
                                                'trainers':
                                               trainers,
                                               'packages':
                                               packages

})

    


def general_profile(request, user_id):
    user = get_object_or_404(CustomUser,id=user_id)
     
     
       
    return render(request, 'Main/general_profile.html', {'user': user})



@login_required
def update_profile(request):
    form = ProfileUpdateForm(instance=request.user)
    form2 = UpdateTrainerInfo(instance=request.user.trainer) if hasattr(request.user, 'trainer') else None

    if request.method == 'POST':
         
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            
          
            form.save()
            messages.success(request, "Profile Updated")
            return redirect('profile')
        else:
             
            messages.error(request, "Form is not Valid")

    return render(request, 'Main/profile.html', {'form': form, 'form2': form2})

@login_required
def ChangeTrainerInfo(request):
    if not hasattr(request.user, 'trainer'):
        return redirect('profile')  # Ensure user has a trainer profile

    trainer = request.user.trainer  # Get the trainer instance

    if request.method == 'POST':
         

        # Pass `request.POST` and `instance=trainer` to bind the form to existing trainer
        form2 = UpdateTrainerInfo(request.POST, instance=trainer)

        if form2.is_valid():
            
            form2.save()
            
            messages.success(request, "Updated!")
            return redirect('profile')  # Redirect to profile after successful update
        else:
            
            messages.error(request, "Form is not valid")

    return render(request, 'Main/profile.html', {'form2': UpdateTrainerInfo(instance=trainer)})  # Re-render the form if GET request


@login_required
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, package__trainer__user=request.user)

    # Prevent approval if payment is still pending
    if booking.payment_status != "paid":
        messages.error(request, "Cannot approve a booking with pending payment.")
         
        return redirect('trainer_bookings')

    booking.status = 'confirmed'
    booking.save()
    messages.success(request, "Booking has been approved.")
    return redirect('trainer_bookings')


@login_required
def reject_booking(request, booking_id):
    """Allow trainers to reject a booking."""
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.package.trainer == request.user:
        booking.status = 'cancelled'
        booking.save()

    return redirect('trainer_bookings')



@login_required
def trainer_bookings(request):
    """Allow trainers to see bookings for their packages."""
    if not hasattr(request.user, 'trainer') or request.user.trainer is None:
        return redirect('profile')  # Redirects only non-trainers

    trainer_packages = Package.objects.filter(trainer=request.user.trainer)  # Use `request.user.trainer`
    bookings = Booking.objects.filter(package__in=trainer_packages).order_by('-booking_date')

    return render(request, 'Main/trainer_bookings.html', {'bookings': bookings})


@login_required
def set_trainer_availability(request):
    """Allow trainers to update their availability."""
    if not hasattr(request.user, 'trainer'):
        return redirect('profile')

    trainer = request.user.trainer
    form = TrainerAvailabilityForm(instance=trainer)

    if request.method == 'POST':
        form = TrainerAvailabilityForm(request.POST, instance=trainer)
        if form.is_valid():
            form.save()
            return redirect('trainer_bookings')

    return render(request, 'Main/set_availability.html', {'form': form})




@login_required
def book_package(request, package_id):
    package = get_object_or_404(Package, id=package_id)

    # Prevent duplicate bookings for the same package by the same user
    if Booking.objects.filter(user=request.user, package=package, status__in=['pending', 'confirmed']).exists():
        messages.error(request, "You have already booked this package.")
         
        return redirect('packages')  

    # Check trainer's availability limit
    if package.trainer:
        start_date = timezone.now().date()
        bookings_on_day = Booking.objects.filter(
            package__trainer=package.trainer,
            start_date__date=start_date
        ).count()

        if bookings_on_day >= package.trainer.max_bookings_per_day:
            messages.error(request, "This trainer is fully booked on this date.")
           
            return redirect('packages')  

    # Create a new booking
    booking = Booking.objects.create(
        user=request.user,
        package=package,
        booking_date=timezone.now(),
        start_date=timezone.now(),
        end_date=timezone.now() + relativedelta(months=package.duration),
        status='pending',
        payment_status='pending'
    )

    messages.success(request, "Booking successful! please make payment to get approved")
    return redirect('my_bookings')  




@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'Main/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.payment_status == "paid":
        messages.error(request, "You cannot cancel a paid booking.")
        return redirect('my_bookings')

    booking.status = "cancelled"
    booking.save()
    messages.success(request, "Your booking has been cancelled successfully.")
    return redirect('my_bookings')

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'Main/change_password.html', {'form': form})


 
def home(request):
    trainers = Trainer.objects.all()
    packages = Package.objects.all()
    return render(request, 'Main/home.html', {
                                                'trainers':
                                               trainers,
                                               'packages':
                                               packages

})


def packages(request):
    trainers = Trainer.objects.all()
    packages = Package.objects.all()
    return render(request, 'Main/packages.html', {
                                                'trainers':
                                               trainers,
                                               'packages':
                                               packages

})




def booked_history(request):
    user = request.user
    booked = Booking.objects.all(user)
    return render(request, 'Main/home.html', {'booked': booked})


from django.shortcuts import render, get_object_or_404
from .models import Trainer, Package

 
def trainer_profile(request, trainer_id):
    """Display trainer's profile and their packages."""
    trainer = get_object_or_404(Trainer, id=trainer_id)  # ✅ Fetch the Trainer instance
    trainer_packages = Package.objects.filter(trainer=trainer)  # ✅ Get only this trainer's packages

    return render(request, 'Main/trainer_profile.html', {
        'trainer': trainer,
        'trainer_packages': trainer_packages
    })



def contact(request):

    return render(request, 'Main/contact.html')






# for payment


PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY


 
def initialize_payment(request, booking_id):
    """Initialize a Paystack payment for a booking."""
    booking = Booking.objects.get(id=booking_id)

    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": request.user.email,
        "amount": int(booking.package.price * 100),  # Convert to kobo
        "callback_url": request.build_absolute_uri(f"/verify-payment/{booking.id}/"),
    }

    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()

    if response_data["status"]:
        return redirect(response_data["data"]["authorization_url"])  # Redirect to Paystack payment page
    return JsonResponse({"error": "Payment initialization failed"}, status=400)


def verify_payment(request, booking_id):
    """Verify a Paystack payment and update the booking/payment status."""
    reference = request.GET.get("reference")
    payment_data = verify_paystack_payment(reference)

    if payment_data and payment_data["status"] == "success":
        booking = Booking.objects.get(id=booking_id)

        # Create a payment record
        Payment.objects.create(
            user=request.user,
            booking=booking,
            amount=booking.package.price,
            transaction_id=reference,
            payment_method="Paystack",
            status="completed",
        )

        # Update booking status to confirmed
        booking.payment_status = "paid"
        booking.status = "confirmed"
        booking.save()

        return render(request , 'Main/payment_success.html')  # Redirect to a success page
    else:
        return render(request , 'Main/payment_failure.html')  # Redirect to a failure page



def custom_404(request, exception):
    print("runining 404")
    return render(request, 'Main/404.html', status=404)