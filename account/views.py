from account.utils import generateRandomToken, sendEmailToken, sendOTPtoEmail
from django.shortcuts import render, redirect
from .models import HotelUser, HotelVendor, Hotel, Amenity, HotelImages
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login
import random




def login_vendor(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return redirect('login_vendor')

        hotel_vendor = HotelVendor.objects.filter(email=email)

        if not hotel_vendor.exists():
            messages.warning(request, "No Account Found.")
            return redirect('login_vendor')

        vendor = hotel_vendor.first()

        if not vendor.is_verified:
            messages.warning(request, "Account not verified. Please check your email.")
            return redirect('login_vendor')

        # Authenticate using the vendor's username
        authenticated_user = authenticate(username=vendor.username, password=password)

        if authenticated_user:
            messages.success(request, "Login Success")
            login(request, authenticated_user)
            return redirect('vdashboard')

        messages.warning(request, "Invalid credentials")
        return redirect('login_vendor')

    return render(request, 'login_vendor.html')

# def login_page(request):
#     if request.method == "POST":
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#
#         hotel_user = HotelUser.objects.filter(email=email)
#
#         if not hotel_user.exists():
#             messages.warning(request, "No account found")
#             return redirect('login_page')  # Fixed: use URL name instead of path
#
#         if not hotel_user[0].is_verified:
#             messages.warning(request, "Account not verified")
#             return redirect('login_page')  # Fixed: use URL name instead of path
#
#         hotel_user = authenticate(username=email, password=password)
#
#         if hotel_user:
#             messages.success(request, "Login successful")
#             login(request, hotel_user)
#             return redirect('login_page')  # Fixed: use URL name instead of path
#
#         messages.warning(request, "Invalid Credentials")
#         return redirect('login_page')  # Fixed: use URL name instead of path
#
#     return render(request, 'login_page.html')


def login_page(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if user exists
        hotel_user_obj = HotelUser.objects.filter(email=email)

        if not hotel_user_obj.exists():
            messages.warning(request, "No account found")
            return redirect('login_page')

        user_obj = hotel_user_obj.first()

        if not user_obj.is_verified:
            messages.warning(request, "Account not verified")
            return redirect('login_page')

        # Use the username field for authentication (which is email in your case)
        authenticated_user = authenticate(username=user_obj.username, password=password)

        if authenticated_user:
            messages.success(request, "Login successful")
            login(request, authenticated_user)
            return redirect('index')  # Redirect to home page after login
        else:
            messages.warning(request, "Invalid Credentials")
            return redirect('login_page')

    return render(request, 'login_page.html')


# def send_otp(request, email):
#     hotel_user = HotelUser.objects.filter(email=email)
#
#     if not hotel_user.exists():
#         messages.warning(request, "No account found")
#         return redirect('login_page')  # Fixed: use URL name
#
#     user = hotel_user.first()
#     if not user.is_verified:
#         messages.warning(request, "Account not verified")
#         return redirect('login_page')  # Fixed: use URL name
#
#     otp = random.randint(1000, 9999)
#     hotel_user.update(otp=otp)
#     sendOTPtoEmail(email, otp)
#     return redirect('verify_otp', email=email)  # Fixed: proper parameter passing

#
# def verify_otp(request, email):
#     if request.method == "POST":
#         otp = request.POST.get('otp')
#         hotel_user = HotelUser.objects.get(email=email)
#
#         if otp == str(hotel_user.otp):
#             messages.success(request, "Login successful")
#             login(request, hotel_user)
#             return redirect('login_page')  # Fixed: use URL name
#         else:
#             messages.warning(request, "Wrong Otp")
#             return redirect('verify_otp', email=email)  # Fixed: proper parameter passing
#
#     return render(request, 'verify_otp.html')


def verify_email_token(request, token):
    try:
        # Try to find the user in HotelUser model first
        hotel_user = HotelUser.objects.get(email_token=token)
        hotel_user.is_verified = True
        hotel_user.email_token = None  # Clear the token after verification
        hotel_user.save()

        messages.success(request, "Email verified successfully! You can now login.")
        return redirect('login_page')

    except HotelUser.DoesNotExist:
        try:
            # Try to find the user in HotelVendor model
            hotel_vendor = HotelVendor.objects.get(email_token=token)
            hotel_vendor.is_verified = True
            hotel_vendor.email_token = None  # Clear the token after verification
            hotel_vendor.save()

            messages.success(request, "Email verified successfully! You can now login as a vendor.")
            return redirect('login_vendor')

        except HotelVendor.DoesNotExist:
            messages.error(request, "Invalid or expired verification link.")
            return redirect('login_page')

    except Exception as e:
        messages.error(request, f"Verification failed: {str(e)}")
        return redirect('login_page')


# Also update your register functions to ensure tokens are properly set
def register_page(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        # Check if user already exists
        hotel_user = HotelUser.objects.filter(
            Q(email=email) | Q(phone_number=phone_number)
        )

        if hotel_user.exists():
            messages.warning(request, "Account exists with Email or Phone Number")
            return redirect('register_page')

        try:
            # Generate token before creating user
            email_token = generateRandomToken()

            hotel_user = HotelUser.objects.create(
                username=email,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                email_token=email_token
            )

            hotel_user.set_password(password)
            hotel_user.save()

            # Send email with proper token
            sendEmailToken(email, email_token)

            messages.success(request, "Registration successful! Please check your email to verify your account.")
            return redirect('register_page')

        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return redirect('register_page')

    return render(request, 'register_page.html')


def register_vendor(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        business_name = request.POST.get('business_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        # Input validation
        if not all([first_name, last_name, business_name, email, password, phone_number]):
            messages.error(request, "All fields are required.")
            return redirect('register_vendor')

        # Check if vendor already exists
        existing_vendor = HotelVendor.objects.filter(
            Q(email=email) | Q(phone_number=phone_number)
        )

        if existing_vendor.exists():
            messages.warning(request, "Account exists with Email or Phone Number.")
            return redirect('register_vendor')

        try:
            # Generate token before creating vendor
            email_token = generateRandomToken()

            # Create new vendor account
            hotel_vendor = HotelVendor.objects.create(
                username=phone_number,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                business_name=business_name,
                email_token=email_token
            )

            hotel_vendor.set_password(password)
            hotel_vendor.save()

            # Send email with proper token
            sendEmailToken(email, email_token)

            messages.success(request, "Registration successful! Please check your email to verify your account.")
            return redirect('register_vendor')

        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return redirect('register_vendor')

    return render(request, 'register_vendor.html')





def send_otp(request, email):
    try:
        # Check if user exists
        hotel_user = HotelUser.objects.filter(email=email)

        if not hotel_user.exists():
            messages.warning(request, "No account found with this email")
            return redirect('login_page')

        user = hotel_user.first()

        if not user.is_verified:
            messages.warning(request, "Account not verified. Please check your email for verification link.")
            return redirect('login_page')

        # Generate and save OTP
        otp = random.randint(1000, 9999)
        hotel_user.update(otp=otp)

        # Send OTP via email
        sendOTPtoEmail(email, otp)

        messages.success(request, f"OTP sent to {email}. Please check your email.")
        return redirect('verify_otp', email=email)

    except Exception as e:
        messages.error(request, f"Error sending OTP: {str(e)}")
        return redirect('login_page')

def verify_otp(request, email):
    try:
        # Check if user exists
        hotel_user_obj = HotelUser.objects.filter(email=email)

        if not hotel_user_obj.exists():
            messages.error(request, "Invalid session. Please try again.")
            return redirect('login_page')

        user_obj = hotel_user_obj.first()

        if request.method == "POST":
            entered_otp = request.POST.get('otp')

            if not entered_otp:
                messages.error(request, "Please enter OTP")
                return redirect('verify_otp', email=email)

            # Compare OTP
            if str(entered_otp) == str(user_obj.otp):
                messages.success(request, "Login successful via OTP")

                # Clear the OTP after successful verification
                user_obj.otp = None
                user_obj.save()

                # Log the user in
                login(request, user_obj)
                return redirect('index')  # Redirect to home page
            else:
                messages.warning(request, "Invalid OTP. Please try again.")
                return redirect('verify_otp', email=email)

        # Pass email to template for context
        return render(request, 'verify_otp.html', {'email': email})

    except Exception as e:
        messages.error(request, f"Error verifying OTP: {str(e)}")
        return redirect('login_page')