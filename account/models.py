from django.db import models
from django.contrib.auth.models import User
class HotelUser(User):
    profile_picture = models.ImageField(upload_to="profile")
    phone_number =  models.CharField(unique = True , max_length= 100)
    email_token = models.CharField(max_length = 100 ,null = True , blank=True)
    otp = models.CharField(max_length = 10 , null = True , blank = True)
    is_verified = models.BooleanField(default = False)


class HotelVendor(User):
    phone_number =  models.CharField(unique = True, max_length= 100)
    business_name = models.CharField(max_length=100, default="my business")
    profile_picture = models.ImageField(upload_to="profile")
    email_token = models.CharField(max_length = 100 ,null = True , blank=True)
    otp = models.CharField(max_length = 10 , null = True , blank = True)

    is_verified = models.BooleanField(default = False)



class Amenity(models.Model):
    name = models.CharField(max_length = 1000)
    icon = models.ImageField(upload_to="hotels")

class Hotel(models.Model):
    hotel_name  = models.CharField(max_length = 100)
    hotel_description = models.TextField()
    hotel_slug = models.SlugField(max_length = 1000 , unique  = True)
    hotel_owner = models.ForeignKey(HotelVendor, on_delete = models.CASCADE , related_name = "hotels")
    amenities= models.ManyToManyField(Amenity)
    hotel_price = models.FloatField()
    hotel_offer_price = models.FloatField()
    hotel_location = models.TextField()
    is_active = models.BooleanField(default = True)

    def __str__(self):
     return self.hotel_name



class HotelImages(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_images')
    image = models.ImageField(upload_to='hotel_images/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.hotel.hotel_name} - Image"

    class Meta:
        ordering = ['-is_primary', '-uploaded_at']

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Remove primary status from other images of same hotel
            HotelImages.objects.filter(hotel=self.hotel, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

class HotelManager(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete = models.CASCADE , related_name = "hotel_managers")
    manager_name = models.CharField(max_length = 100)
    manager_contact = models.CharField(max_length = 100)

class HotelBooking(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete = models.CASCADE , related_name="bookings" )
    booking_user = models.ForeignKey(HotelUser, on_delete = models.CASCADE , )
    booking_start_date = models.DateField()
    booking_end_date = models.DateField()
    price = models.FloatField()