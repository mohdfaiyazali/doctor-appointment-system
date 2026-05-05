from django.shortcuts import render
from .models import DoctorProfile

def doctor_list(request):
    doctors = DoctorProfile.objects.all()

    # 🔍 Get search inputs
    query = request.GET.get('q')
    specialization = request.GET.get('specialization')

    # 🔎 Search by doctor name
    if query:
        doctors = doctors.filter(user__username__icontains=query)

    # 🎯 Filter by specialization
    if specialization:
        doctors = doctors.filter(specialization__icontains=specialization)

    # Get all specializations for dropdown
    specializations = DoctorProfile.objects.values_list('specialization', flat=True).distinct()

    min_exp = request.GET.get('min_exp')
    if min_exp:
        doctors = doctors.filter(experience__gte=min_exp)

    return render(request, 'doctors/doctor_list.html', {
        'doctors': doctors,
        'specializations': specializations
    })