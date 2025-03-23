from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username

    class Meta:
        ordering = ('timestamp',)

class Session(models.Model):
    session_number = models.IntegerField()
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

class UserSessionBet(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    text = models.TextField(default='')

class Voting(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    text = models.TextField(default='')


# wining number
class Allbets(models.Model):
    id = models.AutoField(primary_key=True)
    wining_num = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.wining_num) + ' ' + str(self.timestamp)

    class Meta:
        ordering = ('timestamp',)

class UserWallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pkramount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    trxamount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usdtamount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.user.username


class AddCustomWinningNumber(models.Model):
    wining_num = models.IntegerField()  # null=False is the default, no need to specify
    start_datetime = models.DateTimeField()  # Defines when the winning number starts being valid
    end_datetime = models.DateTimeField()  # Defines when the winning number stops being valid
    confirmed = models.BooleanField(default=True)  # Indicates whether the number is confirmed

    def __str__(self):
        # Updated to show the range of datetime validity
        return f"{self.wining_num} from {self.start_datetime} to {self.end_datetime}"

    class Meta:
        ordering = ('start_datetime',)  # Order by the start of the validity period
