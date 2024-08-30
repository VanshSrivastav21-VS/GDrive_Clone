from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drive import views as drive_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', drive_views.signup, name='signup'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('drive.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)