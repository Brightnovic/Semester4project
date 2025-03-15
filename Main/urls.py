from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('appointment/', views.appointment, name='appointment'),
    path('about/', views.about_us, name='about_us'),
    path('features_benefit/', views.features_benefit, name='features_benefit'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),  # Contact Us page
 
    path('auth/', views.auth_view, name='auth'),  # Combined auth page for login & register
    path('profile/', views.profile, name='profile'),
    path('profile2/', views.profile2, name='profile2'),
    path('trainer-profile/<int:trainer_id>/', views.trainer_profile, name='trainer_profile'),
    path('packages/', views.packages, name='packages'),

    path('update_profile/', views.update_profile, name='update_profile'),
    path('general_profile/<int:user_id>/', views.general_profile, name='general_profile'),
    path('change-password/', views.change_password, name='change_password'),
    #path('booking-history/', views.booking_history, name='booking_history'),
    path('logout/', views.user_logout, name='user_logout'),
    path('book-package/<int:package_id>/', views.book_package, name='book_package'),
    #path('booked_history/', views.booked_history, name='booked_history'),
    path('ChangeTrainerInfo/', views.ChangeTrainerInfo, name='ChangeTrainerInfo'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

    #path('trainers/', views.trainers, name='trainers'),
    path('trainer-bookings/', views.trainer_bookings, name='trainer_bookings'),
    path('approve-booking/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('reject-booking/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    #for payment
    path("pay/<int:booking_id>/", views.initialize_payment, name="initialize_payment"),
    path("verify-payment/<int:booking_id>/", views.verify_payment, name="verify_payment"),
    path('payment-success/pdf/', views.render_pdf_view, {'template_name': 'payment_success.html'}, name='payment_success_pdf'),
    path('payment-failure/pdf/', views.render_pdf_view, {'template_name': 'payment_failure.html'}, name='payment_failure_pdf'),

    #admin reset password
    path('admin/password_reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset'),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('admin/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('admin/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]


from django.urls import get_resolver

 
