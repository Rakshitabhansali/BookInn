from home import views
from django.urls import path

urlpatterns = [
    path('',views.index,name="index"),
    path('vdashboard/', views.vdashboard , name="vdashboard"),
    path('upload-images/<slug:hotel_slug>/', views.upload_images, name='upload_images'),
    path('delete-image/<slug:hotel_slug>/<int:image_id>/', views.delete_image, name='delete_image'),
    path('edit-hotel/<slug:hotel_slug>/', views.edit_hotel, name='edit_hotel'),
    path('set-primary/<slug:hotel_slug>/<int:image_id>/', views.set_primary_image, name='set_primary_image'),
    path('logout_view/' , views.logout_view , name="logout_view"),
    path('detail/<slug>/', views.detail, name="detail"),
    path('add-hotel' , views.add_hotel, name='add_hotel'),
]