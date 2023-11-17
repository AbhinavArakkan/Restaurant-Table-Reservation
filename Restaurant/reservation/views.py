from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm, ReservationForm, ProfilePhotoForm
from django.contrib.auth.decorators import login_required
from . models import Reservation, UserProfile
from django.http import JsonResponse



def login_user(request):    
    if request.method == 'POST':        
        username = request.POST['username']        
        password = request.POST['password']        
        user = authenticate(request, username=username, password=password)        
        if user is not None:            
            login(request, user)            
            return redirect('home')      
        else:            
            error_message = 'Invalid username or password.'    
    else:
          error_message = None    

    return render(request, 'reservation/login.html', {'error_message': error_message})

def logout_user(request):    
    logout(request)    
    return redirect('login')
def home(request):    
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_reservations = Reservation.objects.filter(user=request.user)
    return render(request,'reservation/home.html', {'user_profile': user_profile})


def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  
    else:
        form = UserRegistrationForm()
    return render(request, 'reservation/register.html', {'form': form})


def about(request):
    return render(request, 'reservation/about.html')

def menu(request):
    return render(request, 'reservation/menu.html')

# Define the available tables and their counts
AVAILABLE_TABLES = {
    2: 4,   # Four 2-seated tables
    4: 6,   # Six 4-seated tables
    6: 4,   # Four 6-seated tables
    8: 2    # Two 8-seated tables
}

@login_required
def reservation(request):
    reservation_success = False

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            # Associate the reservation with the current user
            form.instance.user = request.user
            form.user = request.user

            # Check if the requested table is available for the specified date and time
            requested_seats = form.cleaned_data['seats']
            requested_date = form.cleaned_data['reservation_date']
            requested_time = form.cleaned_data['reservation_time']

            # Check if the table is available in the database
            available_tables = Reservation.objects.filter(
                seats=requested_seats,
                reservation_date=requested_date,
                reservation_time=requested_time
            ).count()

            if available_tables < AVAILABLE_TABLES[requested_seats]:
                form.save()
                reservation_success = True
                #form.send_email()
            else:
                # Handle the case when the requested table is not available
                form.add_error('seats', f'No available {requested_seats}-seated tables for the specified date and time.')

    else:
        form = ReservationForm()

    return render(request, 'reservation/reservation.html', {'form': form, 'reservation_success': reservation_success})

def contact(request):
    return render(request, 'reservation/contact.html')



def userinput(request):
    if request.method == 'POST':
        selected_date = request.POST.get('selected_date')
        selected_seats = int(request.POST.get('selected_seats'))

        # Get the total available tables for the selected seats
        total_tables = AVAILABLE_TABLES.get(selected_seats)

        # Get the completely booked times for the selected date and seats
        completely_booked_times = get_completely_booked_times(selected_date, selected_seats, total_tables)

        # Log the selected date, seats, and completely booked times to the console (for demonstration purposes)
        print('Selected Date:', selected_date)
        print('Selected Seats:', selected_seats)
        print('Completely Booked Times:', completely_booked_times)

        # You can perform any additional processing here if needed

        # Return completely_booked_times in JsonResponse
        return JsonResponse({'completely_booked_times': completely_booked_times})

    return JsonResponse({})

def get_completely_booked_times(selected_date, selected_seats, total_tables):
    completely_booked_times = []

    # Loop through each available time
    for time in AVAILABLE_TIMES:
        # Check if the total number of reserved tables for the selected time and seats is equal to the total available tables
        reserved_tables = Reservation.objects.filter(
            reservation_date=selected_date,
            reservation_time=time,
            seats=selected_seats
        ).count()

        if reserved_tables >= total_tables:
            completely_booked_times.append(time)

    return completely_booked_times


# Assuming you have a constant for available times
AVAILABLE_TIMES = [
    '13:00', '14:00', '17:00', '17:30', '18:00', '18:30',
    '19:00', '19:30', '20:00', '20:30', '21:00', '21:30',
    '22:00', '22:30', '23:00', '23:30'
]


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'reservation/profile.html', {'user_profile': user_profile, 'user_reservations': user_reservations})

@login_required
def change_profile_photo(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfilePhotoForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfilePhotoForm(instance=user_profile)
    return render(request, 'reservation/change_profile_photo.html', {'form': form})

@login_required
def upload_profile_photo(request):
    # Check if a UserProfile instance already exists for the user
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # If a profile already exists, update the existing profile
        form = ProfilePhotoForm(request.POST, request.FILES, instance=user_profile)
        
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfilePhotoForm(instance=user_profile)

    return render(request, 'reservation/upload_profile_photo.html', {'form': form})