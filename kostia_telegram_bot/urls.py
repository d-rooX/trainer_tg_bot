from django.contrib import admin
from django.urls import path
from tg_bot.views import webhook, start

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', webhook),
    path('start/', start)
]
