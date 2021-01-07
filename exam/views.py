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
import time
from django.utils import timezone

from .models import Tournament, Question, Answer, Player_Scores

categories = {}


class HomeView(View):
    @method_decorator(login_required)
    def get(self, request):
        current_date = datetime.date.today()
        active = Tournament.objects.filter(start_date__lte=current_date, end_date__gte=current_date)
        upcoming = Tournament.objects.filter(start_date__gt=current_date)

        return render(request, 'exam/index.html', {'active': active, 'upcoming': upcoming})


super = user_passes_test(lambda u: u.is_superuser)


class CreateTournamentView(View):
    @method_decorator(super)
    def get(self, request):
        response = requests.get('https://opentdb.com/api_category.php')
        data = json.loads(response.content)
        for cat in data['trivia_categories']:
            categories["%d" % cat["id"]] = cat['name']
        return render(request, 'exam/create_tourny.html', {'categories': categories})

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
        return render(request, 'exam/index.html', {'active': active, 'upcoming': upcoming})


class LoginView(View):
    def get(self, request):
        return render(request, 'exam/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('exam:index'))
        else:
            return render(request, 'exam/login.html')


class SignUpView(View):
    def get(self, request):
        return render(request, 'exam/signup.html', {})

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if username != "" and password != "" and email != '':
            user = User.objects.create_user(first_name='', last_name='', email='', username=username, password=password)
            user.save()
            return HttpResponseRedirect(reverse('exam:login'))
        else:
            return render(request, 'exam/signup.html')


class LogoutView(View):
    @method_decorator(login_required)
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('exam:login'))


class TournamentView(View):


    @method_decorator(login_required)
    def get(self, request, tournament_id,count):


        current_tournament = Tournament.objects.get(id=tournament_id)

        if Player_Scores.objects.filter(username=request.user.username, tournament=tournament_id).count() < 1:
            new_entry = Player_Scores.objects.create(username=request.user.username, tournament=tournament_id,
                                                     current_question=0, score=0,start_datetime=timezone.now())
            new_entry.save()
        current_user = Player_Scores.objects.get(username=request.user.username, tournament=tournament_id)

        if current_user.current_question < 10:
            questions = Question.objects.filter(tournament=tournament_id).order_by('id')
            question = questions[current_user.current_question]
            answers = Answer.objects.filter(question=question).order_by('?')

            return render(request, 'exam/tournament.html',
                          {'tournament': current_tournament, 'question': question, "answers": answers,
                           'question_num': current_user.current_question + 1})
        else:
            starttime = current_user.start_datetime
            total = timezone.now() - starttime
            return HttpResponseRedirect(reverse('exam:results', kwargs={"score": current_user.score,"ans":total}))

    @method_decorator(login_required)
    def post(self, request):
        count = 1
        current_user = Player_Scores.objects.get(username=request.user.username,
                                                 tournament=request.POST.get("tournament_id"))
        questions = Question.objects.filter(tournament=request.POST.get("tournament_id")).order_by('id')
        question = questions[current_user.current_question]
        question_num = str(current_user.current_question + 1)

        if request.POST.get("answers") == question.correct_ans:
            current_user.score += 1
            messages.success(request, 'You got question %s: Correct!' % question_num)
        else:
            messages.error(request, 'You got question %s: Incorrect and correct answer is %s' % (question_num,question.correct_ans))
        current_user.current_question += 1
        current_user.save()
        count=count+1
        return HttpResponseRedirect(
            reverse('exam:tournament', kwargs={"tournament_id": request.POST.get("tournament_id"),"count":count}))





class ResultsView(View):
    @method_decorator(login_required)
    def get(self, request, score,ans):
        return render(request, 'exam/results.html', {"score": score,"ans":ans})
