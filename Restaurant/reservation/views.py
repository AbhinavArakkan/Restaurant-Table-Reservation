import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm, ReservationForm, ProfilePhotoForm
from django.contrib.auth.decorators import login_required
from . models import Menu, Reservation, UserProfile
from django.http import JsonResponse
from . tasks import send_reservation_details_email_task



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
    return redirect('home')

def get_user_data(request):
    user_profile = None
    user_reservations = None

    if request.user.is_authenticated:
        # Get user profile and reservations for authenticated users
        user_profile = UserProfile.objects.get(user=request.user)
        user_reservations = Reservation.objects.filter(user=request.user)

    return user_profile, user_reservations



def home(request):    
    user_profile, user_reservations = get_user_data(request)
    return render(request,'reservation/home.html', {'user_profile': user_profile})

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Check if a profile photo was provided in the form
            if 'profile_photo' in request.FILES:
                profile_photo = request.FILES['profile_photo']
            else:
                profile_photo = 'profile_photos/profile-picture.png'
            
            # Create or update the UserProfile instance
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.profile_photo = profile_photo
            profile.save()

            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'reservation/register.html', {'form': form})


def about(request):
    user_profile, user_reservations = get_user_data(request)   
    return render(request, 'reservation/about.html', {'user_profile': user_profile})

def menu(request):
    user_profile, user_reservations = get_user_data(request)
    return render(request, 'reservation/menu.html', {'user_profile': user_profile})

# Define the available tables and their counts
AVAILABLE_TABLES = {
    2: 4,   # Four 2-seated tables
    4: 6,   # Six 4-seated tables
    6: 4,   # Four 6-seated tables
    8: 2    # Two 8-seated tables
}

def reservation(request):
    reservation_success = False
    user_profile, user_reservations = get_user_data(request)
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
                form.send_email()

            else:
                # Handle the case when the requested table is not available
                form.add_error('seats', f'No available {requested_seats}-seated tables for the specified date and time.')

    else:
        form = ReservationForm()

    return render(request, 'reservation/reservation.html', {'form': form, 'reservation_success': reservation_success, 'user_profile': user_profile})

def contact(request):
    user_profile, user_reservations = get_user_data(request)
    return render(request, 'reservation/contact.html', {'user_profile': user_profile})

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
    '17:00', '17:30', '18:00', '18:30',
    '19:00', '19:30', '20:00', '20:30', '21:00', '21:30',
    '22:00', '22:30', '23:00', '23:30'
]

@login_required(login_url='login')
def profile(request):


    user_profiles = UserProfile.objects.all()
    user_profile = UserProfile.objects.get(user=request.user)
    user_reservations = get_user_data(request)
    if request.method == 'POST':
        form = ProfilePhotoForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfilePhotoForm(instance=user_profile)


    return render(request, 'reservation/profile.html', {'form': form, 'user_profile': user_profile, 'user_reservations': user_reservations, 'user_profiles': user_profiles})

from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from .models import Reservation

def get_upcoming_reservations(request):
    # Get the current user's reservations
    user_reservations = Reservation.objects.filter(user=request.user)

    # Convert the current date and time to the user's timezone
    current_datetime = timezone.localtime(timezone.now())

    # Filter future reservations based on the current date and time
    future_reservations = user_reservations.filter(
        Q(reservation_date__gt=current_datetime.date()) |
        (Q(reservation_date=current_datetime.date()) & Q(reservation_time__gt=current_datetime.time()))
    ).order_by('reservation_date', 'reservation_time')

    # Convert future_reservations to a list of dictionaries
    upcoming_reservations_data = [
        {
            'reservation_date': reservation.reservation_date.strftime('%Y-%m-%d'),
            'reservation_time': reservation.reservation_time.strftime('%H:%M:%S'),
            'seats': reservation.seats,
            'special_request': reservation.special_request,
            'menu': reservation.menu,
            'qr_code': reservation.qr_code.url,
        }
        for reservation in future_reservations
    ]

    return JsonResponse({'upcoming_reservations': upcoming_reservations_data})



from django.utils import timezone

def get_previous_reservations(request):
    # Get the current user's reservations
    user_reservations = Reservation.objects.filter(user=request.user)

    # Convert the current date and time to the user's timezone
    current_datetime = timezone.localtime(timezone.now())

    # Filter past reservations based on the current date and time
    past_reservations = user_reservations.filter(
        Q(reservation_date__lt=current_datetime.date()) |
        (Q(reservation_date=current_datetime.date()) & Q(reservation_time__lt=current_datetime.time()))
    ).order_by('-reservation_date', '-reservation_time')

    # Convert past_reservations to a list of dictionaries
    previous_reservations_data = [
        {
            'reservation_date': reservation.reservation_date.strftime('%Y-%m-%d'),
            'reservation_time': reservation.reservation_time.strftime('%H:%M:%S'),
            'seats': reservation.seats,
            'special_request': reservation.special_request,
            'menu': reservation.menu,
            'qr_code': reservation.qr_code.url,
        }
        for reservation in past_reservations
    ]

    return JsonResponse({'previous_reservations': previous_reservations_data})


from django.http import JsonResponse

from django.db.models import Q

def get_reservations(request):
    try:
        selected_seats = request.POST.get('selected_seats')
        selected_date = request.POST.get('selected_date')
        selected_time = request.POST.get('selected_time')
        starter = request.POST.get('menu')
        special_request = request.POST.get('special_request')

        reservations = Reservation.objects.all().order_by('-reservation_date', '-reservation_time')

        # Use filter() with multiple conditions
        reservations = reservations.filter(
            Q(seats__in=selected_seats) if selected_seats else Q(),
            Q(reservation_date=selected_date) if selected_date else Q(),
            Q(reservation_time=selected_time) if selected_time else Q()
        )

        # Convert reservations to a list of dictionaries
        reservations_data = [
            {
                'user': {'username': reservation.user.username},
                'seats': reservation.seats,
                'reservation_date': reservation.reservation_date.strftime('%Y-%m-%d'),
                'reservation_time': reservation.reservation_time.strftime('%H:%M:%S'),
                'qr_code': {'url': reservation.qr_code.url},
                'starter': reservation.menu,
                'special_request': reservation.special_request,
            }
            for reservation in reservations
        ]

        return JsonResponse({'reservations': reservations_data})
    except Exception as e:
        # Log the exception for debugging
        print(f"Error in get_reservations view: {e}")
        return JsonResponse({'error': 'An error occurred while fetching reservations.'}, status=500)


def send_reservation_email(request):
    try:
        # Retrieve reservation details from the POST request
        seats = request.POST.get('seats')
        date = request.POST.get('date')
        time = request.POST.get('time')
        qr_code = request.POST.get('qrCode')
        username = request.user.username
        email = request.user.email

        send_reservation_details_email_task.delay(
            username=username,
            email=email,
            seats=seats,
            date=date,
            time=time,
            qr_code=qr_code,
        )


        return JsonResponse({'success': True})
    except Exception as e:
        # Log the exception for debugging
        print(f"Error sending email: {e}")
        return JsonResponse({'error': 'An error occurred while sending the email.'}, status=500)

from django.contrib.auth.views import PasswordResetView

class CustomPasswordResetView(PasswordResetView):
    template_name = 'your_template_name.html'  # Specify your custom template
    email_template_name = 'your_email_template.txt'  # Specify your custom email template
    success_url = 'password_reset_done'  # URL to redirect after successful password reset

def add_food_item(request):
    if request.method == 'POST':
        food_name = request.POST.get('food_name')

        Menu.objects.create(food_name=food_name)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'message': 'Food item added successfully'})
        else:
            return redirect('profile')

    return render(request, 'profile.html')

def fetch_food_items(request):
    # Fetch food items from the database
    food_items = list(Menu.objects.values_list('food_name', flat=True))
    return JsonResponse(food_items, safe=False)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Use csrf_exempt for simplicity. In production, use proper CSRF protection.
def delete_selected_food_items(request):
    if request.method == 'POST':
        selected_food_items = request.POST.getlist('selectedFoodItems[]')

        try:
            # Delete selected food items from the database
            Menu.objects.filter(food_name__in=selected_food_items).delete()

            print("Selected Food Items deleted successfully:", selected_food_items)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            print("Error deleting selected food items:", e)
            return JsonResponse({'status': 'error', 'message': 'Error deleting selected food items'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})