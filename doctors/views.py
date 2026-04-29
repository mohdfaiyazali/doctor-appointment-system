from django.shortcuts import render
from .models import DoctorProfile

def doctor_list(request):
    doctors = DoctorProfile.objects.select_related('user').all()
    return render(request, 'doctors/doctor_list.html', {'doctors': doctors})