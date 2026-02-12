from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from .models import Plan, Code, UserPlan


@login_required
def plans_overview(request):
    """Zeigt alle verfügbaren jährlichen Pläne an."""
    # Pläne holen und Preise berechnen
    plans_raw = Plan.objects.filter(is_active=True).order_by('price')
    
    plans = []
    for plan in plans_raw:
        # Rabatt berechnen
        if plan.discount_percent > 0:
            discount_amount = (plan.discount_percent / Decimal(100)) * plan.price
            discounted = plan.price - discount_amount
        else:
            discounted = plan.price
        
        # Auf 2 Dezimalstellen runden
        plan.discounted_price = discounted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Monatlichen Preis berechnen (12 Monate)
        monthly = plan.discounted_price / Decimal(12)
        plan.monthly_price = monthly.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        plans.append(plan)
    
    # Aktiven Plan holen
    active_plan = UserPlan.objects.filter(
        user=request.user, 
        expires_at__gte=timezone.now()
    ).select_related('plan').first()
    
    # Free Plan als Fallback
    if not active_plan:
        free_plan = Plan.objects.filter(name__icontains="free", is_active=True).first()
        if free_plan:
            free_plan.discounted_price = Decimal('0.00')
            free_plan.monthly_price = Decimal('0.00')
            active_plan = type('DummyUserPlan', (), {
                "plan": free_plan, 
                "expires_at": None
            })()

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