from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Trade
from .services import calculate_profit_loss, get_summary, get_streaks, get_equity_curve, risk_check
from .services import get_trading_score
from django.views.generic import UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum


class LandingView(TemplateView):
    template_name = "trade/landing.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "trade/dashboard.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        trades_all = Trade.objects.filter(user=user,profit_loss__isnull=False).order_by('-created_at')

        context["trades"] = trades_all[:10]

        context["summary"] = get_summary(user)
        context["streaks"] = get_streaks(trades_all)
        context["equity"] = get_equity_curve(trades_all)
        context["risk"] = risk_check(trades_all)

        context["score"] = get_trading_score(
            context["summary"],
            context["streaks"],
            context["risk"]
        )

        return context
    


class TradeListView(LoginRequiredMixin, ListView):
    model = Trade
    template_name = "trade/trade_list.html"
    context_object_name = "trades"
    login_url = "/login/"
    def get_queryset(self):
        return Trade.objects.filter(user=self.request.user,profit_loss__isnull=False).order_by('-created_at')
    



class TradeCreateView(LoginRequiredMixin, CreateView):
    model = Trade
    fields = ['symbol', 'trade_type', 'entry_price', 'exit_price', 'lot_size', 'risk_percent']
    template_name = 'trade/create_trade.html'
    success_url = reverse_lazy('dashboard')
    login_url = "/login/"

    def form_valid(self, form):

        trade = form.save(commit=False)

        trade.user = self.request.user

        trade.save()  # اول save

        trade.profit_loss = calculate_profit_loss(trade)  # بعد محاسبه

        trade.save(update_fields=['profit_loss'])  # دوباره save فقط profit

        return redirect(self.success_url)



class InsightsView(LoginRequiredMixin, TemplateView):
    template_name = "trade/insights.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        trades = Trade.objects.filter(user=user, profit_loss__isnull=False)

        if trades.exists():
            best_trade = max(trades, key=lambda t: float(t.profit_loss))
            worst_trade = min(trades, key=lambda t: float(t.profit_loss))
            avg_profit = sum(float(t.profit_loss) for t in trades) / trades.count()
        else:
            best_trade = worst_trade = None
            avg_profit = 0

        context["best_trade"] = best_trade
        context["worst_trade"] = worst_trade
        context["avg_profit"] = avg_profit

        return context
    

class TradeUpdateView(LoginRequiredMixin, UpdateView):
    model = Trade
    fields = ['symbol', 'trade_type', 'entry_price', 'exit_price', 'lot_size', 'risk_percent']
    template_name = 'trade/edit_trade.html'
    success_url = reverse_lazy('dashboard')
    login_url = "/login/"

    def get_queryset(self):
        return Trade.objects.filter(user=self.request.user)

    def form_valid(self, form):

        trade = form.save(commit=False)

        trade.profit_loss = calculate_profit_loss(trade)

        trade.save()

        return redirect(self.success_url)
    
class TradeDeleteView(LoginRequiredMixin, DeleteView):
    model = Trade
    template_name = 'trade/delete_trade.html'
    success_url = reverse_lazy('dashboard')
    login_url = "/login/"

    def get_queryset(self):
        return Trade.objects.filter(user=self.request.user)
    



def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(username=username, password=password)
        user.save()

        messages.success(request, "Account created successfully")
        return redirect("login")

    return render(request, "registration/register.html")

class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = "trade/analytics.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        trades = Trade.objects.filter(user=user)

        # Total profit
        total_profit = sum(t.profit_loss for t in trades)

        # Best trade
        best_trade = max(trades, key=lambda t: t.profit_loss, default=None)

        # Worst trade
        worst_trade = min(trades, key=lambda t: t.profit_loss, default=None)

        # Win rate
        win_trades = sum(1 for t in trades if t.profit_loss > 0)
        win_rate = (win_trades / trades.count() * 100) if trades.exists() else 0

        # Avg profit
        avg_profit = total_profit / trades.count() if trades.exists() else 0

        context.update({
            "total_profit": total_profit,
            "best_trade": best_trade,
            "worst_trade": worst_trade,
            "win_rate": round(win_rate, 2),
            "avg_profit": round(avg_profit, 2),
        })

        return context

