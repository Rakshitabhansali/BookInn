import uuid
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.contrib.auth import logout
from account.models import Hotel, HotelVendor, Amenity, HotelImages, HotelBooking, HotelUser


def generateSlug(name):
    """Generate a unique slug for hotel"""
    base_slug = slugify(name)
    unique_slug = base_slug + '-' + str(uuid.uuid4())[:8]
    return unique_slug

def index(request):
    hotels = Hotel.objects.all()
    if request.GET.get('search'):
        hotels = hotels.filter(hotel_name__icontains = request.GET.get('search'))

    if request.GET.get('sort_by'):
        sort_by = request.GET.get('sort_by')
        if sort_by == "sort_low":
            hotels = hotels.order_by('hotel_offer_price')
        elif sort_by == "sort_high":
            hotels = hotels.order_by('-hotel_offer_price')
    return render(request, 'index.html', context = {'hotels' : hotels[:50]})


@login_required(login_url='login_vendor')
def vdashboard(request):
    # Retrieve hotels owned by the current vendor
    hotels = Hotel.objects.filter(hotel_owner=request.user)
    context = {'hotels': hotels}
    return render(request, 'vdashboard.html', context)


@login_required(login_url='login_vendor')
def add_hotel(request):
    if request.method == "POST":
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        selected_amenities = request.POST.getlist('amenities')
        hotel_price = request.POST.get('hotel_price')
        hotel_offer_price = request.POST.get('hotel_offer_price')
        hotel_location = request.POST.get('hotel_location')
        hotel_slug = generateSlug(hotel_name)

        try:
            hotel_vendor = HotelVendor.objects.get(id=request.user.id)

            hotel_obj = Hotel.objects.create(
                hotel_name=hotel_name,
                hotel_description=hotel_description,
                hotel_price=hotel_price,
                hotel_offer_price=hotel_offer_price if hotel_offer_price else 0,
                hotel_location=hotel_location,
                hotel_slug=hotel_slug,
                hotel_owner=hotel_vendor
            )

            # Add selected amenities to the hotel
            if selected_amenities:
                for amenity_id in selected_amenities:
                    try:
                        amenity = Amenity.objects.get(id=amenity_id)
                        hotel_obj.amenities.add(amenity)
                    except Amenity.DoesNotExist:
                        continue
                hotel_obj.save()

            messages.success(request, "Hotel Created Successfully!")
            return redirect('vdashboard')  # Fixed: removed the slash

        except HotelVendor.DoesNotExist:
            messages.error(request, "Vendor profile not found.")
        except Exception as e:
            messages.error(request, f"Error creating hotel: {str(e)}")

    # Get all active amenities for the template
    amenities = Amenity.objects.all().order_by('name')
    return render(request, 'add_hotel.html', context={'amenities': amenities})


@login_required(login_url='login_vendor')
def upload_images(request, hotel_slug):
    """View to handle hotel image uploads"""
    try:
        # Get the hotel belonging to the current vendor
        hotel = get_object_or_404(Hotel, hotel_slug=hotel_slug, hotel_owner=request.user)

        if request.method == "POST":
            # Handle multiple image uploads
            uploaded_images = request.FILES.getlist('images')
            alt_texts = request.POST.getlist('alt_text')
            make_primary = request.POST.get('make_primary')

            if not uploaded_images:
                messages.error(request, "Please select at least one image to upload.")
                return redirect('upload_images', hotel_slug=hotel_slug)

            # Process each uploaded image
            for i, image in enumerate(uploaded_images):
                # Validate file type
                if not image.content_type.startswith('image/'):
                    messages.error(request, f"File {image.name} is not a valid image.")
                    continue

                # Validate file size (5MB limit)
                if image.size > 5 * 1024 * 1024:
                    messages.error(request, f"Image {image.name} is too large. Maximum size is 5MB.")
                    continue

                # Get alt text for this image
                alt_text = alt_texts[i] if i < len(alt_texts) else ""

                # Create HotelImage object
                hotel_image = HotelImages.objects.create(
                    hotel=hotel,
                    image=image,
                    alt_text=alt_text,
                    is_primary=False
                )

                # If this is marked as primary, update it
                if make_primary == 'on' and i == 0:
                    HotelImages.objects.filter(hotel=hotel, is_primary=True).update(is_primary=False)
                    hotel_image.is_primary = True
                    hotel_image.save()

            messages.success(request, f"Successfully uploaded {len(uploaded_images)} image(s)!")
            return redirect('upload_images', hotel_slug=hotel_slug)

        # Get existing images for display
        existing_images = HotelImages.objects.filter(hotel=hotel).order_by('-is_primary', '-uploaded_at')

        context = {
            'hotel': hotel,
            'existing_images': existing_images
        }
        return render(request, 'upload_images.html', context)

    except Hotel.DoesNotExist:
        messages.error(request, "Hotel not found or you don't have permission to manage it.")
        return redirect('vdashboard')


@login_required(login_url='login_vendor')
def delete_image(request, hotel_slug, image_id):
    """View to delete a hotel image"""
    if request.method == "POST":
        try:
            hotel = get_object_or_404(Hotel, hotel_slug=hotel_slug, hotel_owner=request.user)
            image = get_object_or_404(HotelImages, id=image_id, hotel=hotel)

            # Delete the image file from storage
            if image.image:
                image.image.delete()

            # Delete the database record
            image.delete()

            messages.success(request, "Image deleted successfully!")

        except Exception as e:
            messages.error(request, f"Error deleting image: {str(e)}")

    return redirect('upload_images', hotel_slug=hotel_slug)


@login_required(login_url='login_vendor')
def set_primary_image(request, hotel_slug, image_id):
    """View to set an image as primary"""
    if request.method == "POST":
        try:
            hotel = get_object_or_404(Hotel, hotel_slug=hotel_slug, hotel_owner=request.user)

            # Remove primary status from all images of this hotel
            HotelImages.objects.filter(hotel=hotel, is_primary=True).update(is_primary=False)

            # Set the selected image as primary
            image = get_object_or_404(HotelImages, id=image_id, hotel=hotel)
            image.is_primary = True
            image.save()

            messages.success(request, "Primary image updated successfully!")

        except Exception as e:
            messages.error(request, f"Error setting primary image: {str(e)}")

    return redirect('upload_images', hotel_slug=hotel_slug)

@login_required(login_url='login_vendor')
def edit_hotel(request, hotel_slug):
    """View to edit hotel details"""
    try:
        hotel_obj = get_object_or_404(Hotel, hotel_slug=hotel_slug)

        # Check if the current user is the owner of the hotel
        if request.user.id != hotel_obj.hotel_owner.id:
            messages.error(request, "You are not authorized to edit this hotel.")
            return redirect('vdashboard')

        if request.method == "POST":
            # Retrieve updated hotel details from the form
            hotel_name = request.POST.get('hotel_name')
            hotel_description = request.POST.get('hotel_description')
            selected_amenities = request.POST.getlist('amenities')
            hotel_price = request.POST.get('hotel_price')
            hotel_offer_price = request.POST.get('hotel_offer_price')
            hotel_location = request.POST.get('hotel_location')

            try:
                # Update hotel object with new details
                hotel_obj.hotel_name = hotel_name
                hotel_obj.hotel_description = hotel_description
                hotel_obj.hotel_price = float(hotel_price) if hotel_price else 0
                hotel_obj.hotel_offer_price = float(hotel_offer_price) if hotel_offer_price else 0
                hotel_obj.hotel_location = hotel_location

                # Update amenities
                hotel_obj.amenities.clear()  # Clear existing amenities
                if selected_amenities:
                    for amenity_id in selected_amenities:
                        try:
                            amenity = Amenity.objects.get(id=amenity_id)
                            hotel_obj.amenities.add(amenity)
                        except Amenity.DoesNotExist:
                            continue

                hotel_obj.save()

                messages.success(request, "Hotel Details Updated Successfully!")
                return HttpResponseRedirect(request.path_info)

            except ValueError:
                messages.error(request, "Please enter valid price values.")
            except Exception as e:
                messages.error(request, f"Error updating hotel: {str(e)}")

        # Retrieve amenities for rendering in the template
        amenities = Amenity.objects.all().order_by('name')

        # Get current hotel amenities for pre-selection
        current_amenities = hotel_obj.amenities.all()

        # Render the edit_hotel.html template with hotel and amenities as context
        return render(request, 'edit_hotel.html', context={
            'hotel': hotel_obj,
            'amenities': amenities,
            'current_amenities': current_amenities
        })

    except Hotel.DoesNotExist:
        messages.error(request, "Hotel not found.")
        return redirect('vdashboard')


def logout_view(request):
    logout(request)
    messages.success(request,"Logged Out successfully")
    return redirect('login_page')

def detail(request, slug):
    hotel = Hotel.objects.get(hotel_slug = slug)

    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_date = datetime.strptime(start_date , '%Y-%m-%d')
        end_date = datetime.strptime(end_date , '%Y-%m-%d')
        days_count = (end_date - start_date).days

        if days_count <= 0:
            messages.warning(request, "Invalid Booking Date.")
            return HttpResponseRedirect(request.path_info)

        HotelBooking.objects.create(
            hotel = hotel,
            booking_user = HotelUser.objects.get(id = request.user.id),
            booking_start_date = start_date,
            booking_end_date =end_date,
            price = hotel.hotel_offer_price * days_count
        )
        messages.warning(request, "Booking Captured.")

        return HttpResponseRedirect(request.path_info)


    return render(request, 'detail.html', context = {'hotel' : hotel})