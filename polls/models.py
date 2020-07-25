from django.db import models


class Tournament(models.Model):
    DIFFICULTY = (
        ('E', 'Easy'),
        ('M', 'Medium'),
        ('H', 'Hard'),
    )

    name = models.CharField(
        max_length=100,
        default='')

    start_date = models.DateField()

    end_date = models.DateField()

    category = models.CharField(
        max_length=200,
        default='Any Category')

    difficulty = models.CharField(
        max_length=100,
        choices=DIFFICULTY,
        default='Easy')


class Question(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    correct_ans = models.CharField(max_length=200)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=200)


class Player_Scores(models.Model):
    username = models.CharField(max_length=200)
    tournament = models.IntegerField()
    current_question = models.IntegerField()
    score = models.IntegerField()
