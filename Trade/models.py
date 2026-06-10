from django.db import models
from django.db import models
from django.contrib.auth.models import User


class Trade(models.Model):

    TRADE_TYPES = (('BUY', 'Buy'),('SELL', 'Sell'),)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='trades')

    symbol = models.CharField(max_length=10, default="EURUSD")

    trade_type = models.CharField(max_length=10,choices=TRADE_TYPES)

    entry_price = models.DecimalField(max_digits=10,decimal_places=5, null=True,blank=True)

    exit_price = models.DecimalField(max_digits=10,decimal_places=5,null=True,blank=True)

    lot_size = models.DecimalField(max_digits=10,decimal_places=2)
    is_open = models.BooleanField(default=True)


    profit_loss = models.DecimalField(max_digits=15,decimal_places=5,blank=True,null=True)

    risk_percent = models.FloatField(default=1.0)

    created_at = models.DateTimeField(auto_now_add=True)



class Feedback(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username}"