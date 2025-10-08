from django.urls import path
from .views import status

urlpatterns = [path("status/", status, name="edge_isr_status")]
