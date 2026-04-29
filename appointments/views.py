from django.shortcuts import render, redirect, get_object_or_404
from .models import Appointment
from doctors.models import DoctorProfile
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import time


User = get_user_model()


@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by('-date', '-time')
    return render(request, 'appointments/my_appointments.html', {
        'appointments': appointments
    })


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    appointment.status = 'cancelled'
    appointment.save()
    return redirect('my_appointments')



def generate_time_slots():
    slots = []
    start_hour = 10
    end_hour = 17

    for hour in range(start_hour, end_hour):
        slots.append(time(hour, 0))
        slots.append(time(hour, 30))

    return slots

@login_required
def book_appointment(request, doctor_id):
    doctor_profile = get_object_or_404(DoctorProfile, id=doctor_id)
    doctor = doctor_profile.user

    selected_date = request.GET.get('date')

    booked_slots = []
    all_slots = generate_time_slots()

    if selected_date:
        booked_slots = list(
            Appointment.objects.filter(
                doctor=doctor,
                date=selected_date
            ).values_list('time', flat=True)
        )

    if request.method == 'POST':
        date = request.POST.get('date')
        time_selected = request.POST.get('time')

        exists = Appointment.objects.filter(
            doctor=doctor,
            date=date,
            time=time_selected
        ).exists()

        if exists:
            messages.error(request, "This slot is already booked!")
        else:
            Appointment.objects.create(
                patient=request.user,
                doctor=doctor,
                date=date,
                time=time_selected
            )
            messages.success(request, "Appointment booked successfully!")
            return redirect('doctor_list')

    return render(request, 'appointments/book_appointment.html', {
        'doctor': doctor,
        'booked_slots': booked_slots,
        'selected_date': selected_date,
        'all_slots': all_slots
    })