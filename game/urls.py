from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('Game/Player_Vs_AI', views.player_vs_ai, name='start_player_vs_ai'),
    path('Game/AI_vs_Player', views.ai_vs_player, name='start_ai_vs_player'),
    path('<int:round>/SubmitFeedback/<colors>', views.submit_feedback, name='submit_feedback'),
    path('SubmitColors/<ronde>/<colors>', views.submit_colors, name='submit_colors'),
    path('CheckColors/<ronde>/<ai_comb>/<colors>', views.check_colors, name='check_colors'),
]