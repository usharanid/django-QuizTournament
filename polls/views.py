from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import (authenticate, login, logout, )
from django.views.generic import View
from django.http import HttpResponseRedirect
import json
import datetime
from django.contrib import messages
import requests

from .models import Tournament, Question, Answer, Player_Scores

categories = {}


class HomeView(View):
    @method_decorator(login_required)
    def get(self, request):
        current_date = datetime.date.today()
        active = Tournament.objects.filter(start_date__lte=current_date, end_date__gte=current_date)
        upcoming = Tournament.objects.filter(start_date__gt=current_date)

        return render(request, 'polls/index.html', {'active': active, 'upcoming': upcoming})


super = user_passes_test(lambda u: u.is_superuser)


class CreateTournamentView(View):
    @method_decorator(super)
    def get(self, request):
        response = requests.get('https://opentdb.com/api_category.php')
        data = json.loads(response.content)
        for cat in data['trivia_categories']:
            categories["%d" % cat["id"]] = cat['name']
        return render(request, 'polls/create_tourny.html', {'categories': categories})

    @method_decorator(super)
    def post(self, request):
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        difficulty = request.POST.get('difficulty').lower()
        category = request.POST.get('category')

        response = requests.get(
            'https://opentdb.com/api.php?amount=10&category=%s&difficulty=%s' % (category, difficulty))
        data = json.loads(response.content)
        if data['response_code'] == 0:
            tournament = Tournament.objects.create(name=name, start_date=start_date, end_date=end_date,
                                                   difficulty=difficulty, category=categories.get("%s" % category))
            tournament.save()
            for q in data['results']:
                question = Question.objects.create(tournament=tournament, question_text=q["question"],
                                                   correct_ans=q["correct_answer"])
                answer = Answer.objects.create(question=question, answer_text=q["correct_answer"])
                answer.save()
                for ans in q["incorrect_answers"]:
                    answer = Answer.objects.create(question=question, answer_text=ans)
                    answer.save()
        current_date = datetime.date.today()
        active = Tournament.objects.filter(start_date__lte=current_date, end_date__gte=current_date)
        upcoming = Tournament.objects.filter(start_date__gt=current_date)
        return render(request, 'polls/index.html', {'active': active, 'upcoming': upcoming})


class LoginView(View):
    def get(self, request):
        return render(request, 'polls/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('polls:index'))
        else:
            return render(request, 'polls/login.html')


class SignUpView(View):
    def get(self, request):
        return render(request, 'polls/signup.html', {})

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if username != "" and password != "" and email != '':
            user = User.objects.create_user(first_name='', last_name='', email='', username=username, password=password)
            user.save()
            return HttpResponseRedirect(reverse('polls:login'))
        else:
            return render(request, 'polls/signup.html')


class LogoutView(View):
    @method_decorator(login_required)
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('polls:login'))


class TournamentView(View):
    @method_decorator(login_required)
    def get(self, request, tournament_id):

        current_tournament = Tournament.objects.get(id=tournament_id)

        if Player_Scores.objects.filter(username=request.user.username, tournament=tournament_id).count() < 1:
            new_entry = Player_Scores.objects.create(username=request.user.username, tournament=tournament_id,
                                                     current_question=0, score=0)
            new_entry.save()
        current_user = Player_Scores.objects.get(username=request.user.username, tournament=tournament_id)

        if current_user.current_question < 10:
            questions = Question.objects.filter(tournament=tournament_id).order_by('id')
            question = questions[current_user.current_question]
            answers = Answer.objects.filter(question=question).order_by('?')

            return render(request, 'polls/tournament.html',
                          {'tournament': current_tournament, 'question': question, "answers": answers,
                           'question_num': current_user.current_question + 1})
        else:
            return HttpResponseRedirect(reverse('polls:results', kwargs={"score": current_user.score}))

    @method_decorator(login_required)
    def post(self, request):
        current_user = Player_Scores.objects.get(username=request.user.username,
                                                 tournament=request.POST.get("tournament_id"))
        questions = Question.objects.filter(tournament=request.POST.get("tournament_id")).order_by('id')
        question = questions[current_user.current_question]
        question_num = str(current_user.current_question + 1)

        if request.POST.get("answers") == question.correct_ans:
            current_user.score += 1
            messages.success(request, 'You got question %s: Correct!' % question_num)
        else:
            messages.error(request, 'You got question %s: Incorrect' % question_num)
        current_user.current_question += 1
        current_user.save()

        return HttpResponseRedirect(
            reverse('polls:tournament', kwargs={"tournament_id": request.POST.get("tournament_id")}))


class HighscoresView(View):
    def get(self, request):
        high_scores = []
        all_scores = Player_Scores.objects.filter(current_question=10)
        for s in all_scores:
            filtered_scores = Player_Scores.objects.filter(tournament=s.tournament).order_by('-score')
            high_scores.append(filtered_scores[0])
        scores = list(set(high_scores))
        tournaments = Tournament.objects.all()
        return render(request, 'polls/highscores.html', {"highscores": scores, "tournaments": tournaments})


class ResultsView(View):
    @method_decorator(login_required)
    def get(self, request, score):
        return render(request, 'polls/results.html', {"score": score})
