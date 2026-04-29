from django.urls import path
from .views import book_appointment, my_appointments, cancel_appointment

urlpatterns = [
    path('book/<int:doctor_id>/', book_appointment, name='book_appointment'),
    path('my/', my_appointments, name='my_appointments'),
    path('cancel/<int:appointment_id>/', cancel_appointment, name='cancel_appointment'),
]