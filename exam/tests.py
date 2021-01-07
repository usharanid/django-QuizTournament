from django.test import TestCase

from .models import Tournament, Question, Answer, Player_Scores
from exam import views
from django.contrib.auth.models import User


class TestHomeView(TestCase):
    def setUp(self):
        User.objects.create_user(username="user", password="pass")
        User.objects.create_superuser(username="super", email="test@gmail.com", password="pass")

    def test_call_index_denies_anonymous(self):
        response = self.client.get('/exam/index/', follow=True)
        self.assertRedirects(response, '/exam/login/?next=/exam/index/')


class TestCreateView(TestCase):
    def setUp(self):
        User.objects.create_user(username="user", password="pass")
        User.objects.create_superuser(username="super", email="test@gmail.com", password="pass")

    def test_call_view_loads_create(self):
        self.client.login(username='super', password='pass')
        response = self.client.get('/exam/create/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exam/create_tourny.html')

    def test_call_view_loads_create_post(self):
        self.client.login(username='super', password='pass')
        args = {'name': 'name_test', 'start_date': '2018-06-19', 'end_date': '2018-06-27', 'difficulty': 'Easy',
                'category': 'Sport'}
        response = self.client.post('/exam/create/', args, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exam/index.html')


class TestLoginView(TestCase):
    def setUp(self):
        User.objects.create_user(username="user", password="pass")
        User.objects.create_superuser(username="super", email="test@gmail.com", password="pass")

    def test_login_get(self):
        response = self.client.get('/exam/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exam/login.html')

    def test_login_post_pass(self):
        args = {'username': 'user', 'password': 'pass'}
        response = self.client.post('/exam/login/', args, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exam/index.html')

    def test_login_post_fail(self):
        args = {'username': 'dfsgsfg', 'password': 'pass'}
        response = self.client.post('/exam/login/', args, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exam/login.html')


class TestSignUpView(TestCase):
    def test_signup_get(self):
        response = self.client.get('/exam/signup/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exam/signup.html')

    def test_signup_pass(self):
        args = {'username': 'user', 'password': 'pass'}
        response = self.client.post('/exam/signup/', args, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exam/login.html')

    def test_signup_fail(self):
        args = {'username': '', 'password': ''}
        response = self.client.post('/exam/signup/', args, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exam/signup.html')


class TestTournamentView(TestCase):
    def setUp(self):
        tournament = Tournament.objects.create(name="testTournament", start_date='2018-06-20', end_date='2018-06-27',
                                               difficulty="easy", category="Sports")
        tournament.save()
        questions = ["q1", "q2", "q3"]
        answers = ["a1", "a2", "a3"]
        for q in questions:
            question = Question.objects.create(tournament=tournament, question_text=q,
                                               correct_ans=answers[0])
            answer = Answer.objects.create(question=question, answer_text=answers[0])
            answer.save()
            for a in answers:
                answer = Answer.objects.create(question=question, answer_text=a)
                answer.save()
            question.save()

        User.objects.create_user(username="user", password="pass")
        User.objects.create_user(username="test", password="pass")
        User.objects.create_superuser(username="super", email="test@gmail.com", password="pass")

    def test_tournament_get(self):
        self.client.login(username='user', password='pass')
        tournament = Tournament.objects.get(name="testTournament")
        response = self.client.get('/exam/tournament/%d' % tournament.id, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exam/tournament.html')

    def test_tournament_get_completed(self):
        self.client.login(username='user', password='pass')
        tournament = Tournament.objects.get(name="testTournament")
        current_user = Player_Scores.objects.create(username="user", tournament=tournament.id, current_question=10,
                                                    score=0)
        current_user.save()
        response = self.client.get('/exam/tournament/%d' % tournament.id, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exam/results.html')

    def test_tournament_post(self):
        self.client.login(username='test', password='pass')
        tournament = Tournament.objects.get(name="testTournament")
        current_user = Player_Scores.objects.create(username="test", tournament=tournament.id, current_question=0,
                                                    score=0)
        current_user.save()
        response = self.client.post('/exam/tournament/%d' % tournament.id, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exam/tournament.html')


class TestLogoutView(TestCase):
    def test_signup_get(self):
        self.client.login(username='user', password='pass')
        response = self.client.get('/exam/logout/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exam/login.html')


class TestViewLoads(TestCase):
    def setUp(self):
        User.objects.create_user(username="user", password="pass")
        User.objects.create_superuser(username="super", email="test@gmail.com", password="pass")

    def test_call_view_loads(self):
        self.client.login(username='user', password='pass')
        response = self.client.get('/exam/index/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exam/index.html')

    def test_results(self):
        from django.urls import reverse
        response = self.client.get(reverse('exam:login'), format='json')
        self.assertEqual(response.status_code, 200)


class TestResultView(TestCase):
    def setUp(self):
        User.objects.create_user(username="user", password="pass")
        User.objects.create_superuser(username="super", email="test@gmail.com", password="pass")

    def test_result_get(self):
        self.client.login(username='user', password='pass')
        response = self.client.get('/exam/scores/10', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exam/results.html')
