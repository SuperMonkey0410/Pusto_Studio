from django.db import models
from django.utils import timezone
import csv
from io import StringIO
from datetime import date

""""Задание 1 """
class Player(models.Model): # Модель Игрока
    username = models.CharField(max_length=150, unique=True, verbose_name='Никнейм')
    first_login = models.DateTimeField(auto_now_add=True, verbose_name='Дата первого захода')
    last_login = models.DateTimeField(auto_now=True, verbose_name='Дата последнего захода')
    points = models.IntegerField(default=0, verbose_name='Количество очков')

    def __str__(self):
        return self.username

    def add_points(self, points):
        self.points += points
        self.save()


class Boost(models.Model):  # Модель бонуса
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='boosts')
    boost_type = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    obtained_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.boost_type} for {self.player.username} (x{self.quantity})"

    def add_boost(self, quantity):
        self.quantity += quantity
        self.save()



""""Задание 2 """


class Player(models.Model):
    player_id = models.CharField(max_length=100)


class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)


class Prize(models.Model):
    title = models.CharField()


class PlayerLevel(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField()
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)


class LevelPrize(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateField()

    def assign_prize_to_player(player_id, level_id, prize_id):
        player = Player.objects.get(player_id=player_id)
        level = Level.objects.get(id=level_id)
        prize = Prize.objects.get(id=prize_id)

        player_level = PlayerLevel.objects.get(player=player, level=level)

        if not player_level.is_completed:
            player_level.is_completed = True
            player_level.completed = date.today()
            player_level.save()

            LevelPrize.objects.create(level=level, prize=prize, received=date.today())

    def export_data_to_csv():
        fields = ['player_id', 'level_title', 'is_completed', 'prize_title']

        buffer = StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fields)
        writer.writeheader()

        player_levels = PlayerLevel.objects.select_related('player', 'level', 'prize').filter(is_completed=True)

        for player_level in player_levels:
            writer.writerow({
                'player_id': player_level.player.player_id,
                'level_title': player_level.level.title,
                'is_completed': player_level.is_completed,
                'prize_title': player_level.level.levelprize.prize.title
            })

        return buffer.getvalue()