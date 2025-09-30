from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Plan, Code, UserPlan


@login_required
def plans_overview(request):
    """Zeigt alle verfügbaren Pläne an und den aktuell aktiven Plan des Users."""
    plans = Plan.objects.filter(is_active=True)
    active_plan = UserPlan.objects.filter(user=request.user, expires_at__gte=timezone.now()).first()
    return render(request, "plans/overview.html", {
        "plans": plans,
        "active_plan": active_plan
    })


@login_required
def redeem_code(request):
    """Einlösen eines Codes zur Aktivierung eines Plans."""
    msg = None
    if request.method == "POST":
        code_text = request.POST.get("code", "").strip()
        try:
            code = Code.objects.get(code=code_text)
            ok, result = UserPlan.activate_code(request.user, code)
            if ok:
                msg = "✅ Plan erfolgreich aktiviert!"
            else:
                msg = f"⚠️ {result}"
        except Code.DoesNotExist:
            msg = "❌ Code ungültig."
    return render(request, "plans/redeem_code.html", {"msg": msg})
