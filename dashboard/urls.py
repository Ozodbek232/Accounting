from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from common import views
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include('common.urls')),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

