from django.urls import path
from django.conf.urls import url

from . import views
from exam.views import HomeView, CreateTournamentView, LoginView, SignUpView, TournamentView, LogoutView,  ResultsView

app_name = 'exam'
urlpatterns = [
    path('tournament/<int:tournament_id>/<int:count>', TournamentView.as_view(), name='tournament'),
    #path('', TournamentView.as_view(), name='check_answer'),
    path('', LoginView.as_view()),
    path('check', TournamentView.as_view(), name='check_answer'),
    path('create/', CreateTournamentView.as_view(), name='create'),
    path('create_tourny/', CreateTournamentView.as_view(), name='create_tourny'),
    path('index/', HomeView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('', SignUpView.as_view(), name='create_user'),
    path('scores/<int:score>/<str:ans>/', ResultsView.as_view(), name='results'),
]
