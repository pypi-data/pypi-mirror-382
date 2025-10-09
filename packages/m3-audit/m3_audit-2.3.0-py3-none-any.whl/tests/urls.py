from django.urls import (
    include,
    path,
)
from m3.helpers import (
    urls,
)


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    # Example:
    # path('', your_view_function),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # path('admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    # path('admin/', admin.site.urls),
]

urlpatterns += urls.get_app_urlpatterns()
