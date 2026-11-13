from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('auth/', include('users.urls')),
    path('api/platform/', include('control_plane.urls')),
    path('api/contributions/', include('contributions.urls')),
    path('contributions/', include('contributions.urls')),
    path('api/api/contributions/', include('contributions.urls')),
    path('api/populate/', include(('populate_core.urls', 'populate'), namespace='populate')),
    path('populate/', include(('populate_core.urls', 'populate-direct'), namespace='populate-direct')),
]
