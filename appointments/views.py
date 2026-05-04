from django.shortcuts import render, redirect, get_object_or_404
from .models import Appointment
from doctors.models import DoctorProfile
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, time, date
from .decorators import doctor_required

User = get_user_model()


@doctor_required
def doctor_dashboard(request):
    # Only allow doctors
    if request.user.role != 'doctor':
        return redirect('doctor_list')

    appointments = Appointment.objects.filter(
        doctor=request.user
    ).order_by('-date', '-time')

    return render(request, 'appointments/doctor_dashboard.html', {
        'appointments': appointments
    })


@login_required
def update_status(request, appointment_id, status):
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=request.user  # ensure doctor owns it
    )

    if status in ['confirmed', 'cancelled', 'completed']:
        appointment.status = status
        appointment.save()

    return redirect('doctor_dashboard')


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

    # ✅ Convert selected_date to proper date object
    selected_date_obj = None
    if selected_date:
        try:
            selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()

            booked_slots = list(
                Appointment.objects.filter(
                    doctor=doctor,
                    date=selected_date_obj
                ).values_list('time', flat=True)
            )
        except ValueError:
            selected_date_obj = None

    # ✅ Handle POST (Booking)
        if request.method == 'POST':
            date_str = request.POST.get('date')
            time_str = request.POST.get('time')

            try:
                selected_date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                selected_time_obj = datetime.strptime(time_str, "%H:%M").time()
            except (ValueError, TypeError):
                messages.error(request, "Invalid date or time format")
                return redirect(request.path)

            # ❌ Past date check
            if selected_date_obj < date.today():
                messages.error(request, "Cannot book past dates")
                return redirect(request.path + f"?date={date_str}")

            # ❌ Past time check (for today)
            if selected_date_obj == date.today():
                current_time = datetime.now().time()
                if selected_time_obj < current_time:
                    messages.error(request, "Cannot book past time")
                    return redirect(request.path + f"?date={date_str}")

            # ❌ Double booking check
            if Appointment.objects.filter(
                doctor=doctor,
                date=selected_date_obj,
                time=selected_time_obj
            ).exists():
                messages.error(request, "This slot is already booked")
                return redirect(request.path + f"?date={date_str}")

            # ✅ Create appointment
            Appointment.objects.create(
                patient=request.user,
                doctor=doctor,
                date=selected_date_obj,
                time=selected_time_obj
            )

            messages.success(request, "Appointment booked successfully!")
            return redirect('doctor_list')

    return render(request, 'appointments/book_appointment.html', {
        'doctor': doctor,
        'booked_slots': booked_slots,
        'selected_date': selected_date,
        'all_slots': all_slots
    })