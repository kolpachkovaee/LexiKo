"""URL patterns for LexiKo trainer."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('cards/', views.card_list, name='card_list'),
    path('cards/add/', views.card_add, name='card_add'),
    path('cards/import/', views.import_cards, name='import_cards'),
    path('cards/<str:card_id>/edit/', views.card_edit, name='card_edit'),
    path('cards/<str:card_id>/delete/', views.card_delete, name='card_delete'),
    path('cards/<str:card_id>/', views.card_detail, name='card_detail'),
    path('study/', views.study, name='study'),
    path('quiz/', views.quiz, name='quiz'),
    path('stats/', views.stats, name='stats'),
    path('api/answer/', views.api_record_answer, name='api_record_answer'),
    path('api/cards/<str:card_id>/drawing/', views.api_save_drawing, name='api_save_drawing'),
]
