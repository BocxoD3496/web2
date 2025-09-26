from django.urls import path
from . import views

app_name = "study"

urlpatterns = [
    path("", views.index, name="index"),
    path("lesson/<str:lesson_id>/", views.lesson_detail, name="lesson_detail"),
    path("lesson/<str:lesson_id>/submit/", views.submit_test, name="submit_test"),
    path("save/", views.save_progress, name="save_progress"),
    path("reset/", views.reset_progress, name="reset_progress"),
]
