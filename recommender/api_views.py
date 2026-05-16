import json
import calendar
from datetime import date, datetime, timedelta
from collections import Counter
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.middleware.csrf import get_token
from recommender.models import Food, UserList, SavedDiet, UserPreference, FavoriteFood, WaterLog
from recommender.functions import Weight_Gain, Weight_Loss, Healthy, calculate_bmr, chatfunction


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _calculate_body_fat_percentage(weight_kg, height_cm, age, gender):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m * height_m)
    if gender == "female":
        return (1.20 * bmi) + (0.23 * age) - 5.4
    return (1.20 * bmi) + (0.23 * age) - 16.2


def _serialize_foods(queryset):
    return [
        {
            "id": f.id,
            "name": f.name,
            "cal": f.cal,
            "fat": f.fat,
            "pro": f.pro,
            "sug": f.sug,
            "imagepath": f.imagepath,
        }
        for f in queryset
    ]


def _normalize_period(value):
    value = (value or "").strip().lower()
    if value in {"daily", "weekly", "monthly"}:
        return value
    return "daily"


def _parse_plan_date(value):
    if not value:
        return date.today()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return date.today()


def _record_plan_date(record):
    return record.plan_date or record.created_at.date()


def _ensure_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _owner_lookup(request):
    if request.user.is_authenticated:
        return {"user": request.user}
    return {"user__isnull": True, "session_key": _ensure_session_key(request)}


def _owner_create(request):
    if request.user.is_authenticated:
        return {"user": request.user}
    return {"user": None, "session_key": _ensure_session_key(request)}


def _period_days(period, plan_date):
    if period == "weekly":
        return 7
    if period == "monthly":
        return calendar.monthrange(plan_date.year, plan_date.month)[1]
    return 1


def _parse_int(value):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def csrf_token_view(request):
    return JsonResponse({"csrfToken": get_token(request)})


@require_GET
def auth_status(request):
    if request.user.is_authenticated:
        return JsonResponse({
            "is_authenticated": True,
            "user": {
                "username": request.user.username,
                "email": request.user.email,
            }
        })
    return JsonResponse({"is_authenticated": False})


@csrf_exempt
@require_POST
def api_login(request):
    data = _parse_json_body(request)
    if not data:
        return JsonResponse({"ok": False, "message": "Invalid request"}, status=400)

    username = (data.get("username") or "").strip()
    password = data.get("password", "")

    if not username or not password:
        return JsonResponse({"ok": False, "message": "Username and password are required"}, status=400)

    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({
            "ok": True,
            "user": {"username": user.username, "email": user.email}
        })
    return JsonResponse({"ok": False, "message": "Invalid username or password"}, status=401)


@csrf_exempt
@require_POST
def api_signup(request):
    data = _parse_json_body(request)
    if not data:
        return JsonResponse({"ok": False, "message": "Invalid request"}, status=400)

    username = (data.get("username") or "").strip()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")
    email = (data.get("email") or "").strip().lower()

    if not username or not password or not email:
        return JsonResponse({"ok": False, "message": "All fields are required"}, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"ok": False, "message": "Invalid email address"}, status=400)

    if len(password) < 6:
        return JsonResponse({"ok": False, "message": "Password must be at least 6 characters"}, status=400)

    if password != confirm_password:
        return JsonResponse({"ok": False, "message": "Passwords do not match"}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"ok": False, "message": "Username already exists"}, status=400)

    if User.objects.filter(email=email).exists() or UserList.objects.filter(mail_id1=email).exists():
        return JsonResponse({"ok": False, "message": "Email already exists"}, status=400)

    try:
        new_user = User.objects.create_user(username=username, email=email, password=password)
        UserList.objects.create(Username=username, Password=password, mail_id1=email)
    except IntegrityError:
        return JsonResponse({"ok": False, "message": "Unable to create account"}, status=400)

    login(request, new_user)
    return JsonResponse({
        "ok": True,
        "user": {"username": new_user.username, "email": new_user.email}
    })


@csrf_exempt
@require_POST
def api_logout(request):
    logout(request)
    return JsonResponse({"ok": True})


@csrf_exempt
@require_POST
def api_recommend(request):
    data = _parse_json_body(request)
    if not data:
        return JsonResponse({"ok": False, "message": "Invalid request"}, status=400)

    try:
        age = int(data.get("age"))
        weight = int(data.get("weight"))
        height = int(data.get("height"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "message": "Age, weight, height are required numbers"}, status=400)

    goal = data.get("goal", "healthy")
    activity = data.get("activity", "Heavy")
    gender = data.get("gender")
    category = data.get("category", "none")
    bodyfat_raw = data.get("bodyfat")

    if not gender:
        return JsonResponse({"ok": False, "message": "Gender is required"}, status=400)

    if bodyfat_raw:
        bodyfat = float(bodyfat_raw)
        bodyfat_source = "manual"
    else:
        bodyfat = _calculate_body_fat_percentage(weight, height, age, gender)
        bodyfat_source = "calculated"

    bodyfat = round(bodyfat, 2)
    bmr = calculate_bmr(weight, height, age, gender, activity, category)
    maintaincalories = int(bmr)

    finaldata = []
    bmi = 0
    bmiinfo = ""

    if goal == "weight gain":
        finaldata = Weight_Gain(age, weight, height)
    elif goal == "weight loss":
        finaldata = Weight_Loss(age, weight, height)
    else:
        finaldata = Healthy(age, weight, height)

    bmi = int(finaldata[-2])
    bmiinfo = finaldata[-1]

    if goal == "weight gain":
        caloriesreq = maintaincalories + 400
    elif goal == "weight loss":
        caloriesreq = maintaincalories - 750
    else:
        caloriesreq = maintaincalories

    breakfast = Food.objects.filter(bf=1, name__in=finaldata)
    lunch = Food.objects.filter(lu=1, name__in=finaldata)
    dinner = Food.objects.filter(di=1, name__in=finaldata)

    return JsonResponse({
        "ok": True,
        "breakfast": _serialize_foods(breakfast),
        "lunch": _serialize_foods(lunch),
        "dinner": _serialize_foods(dinner),
        "bmi": bmi,
        "bmiinfo": bmiinfo,
        "caloriesreq": caloriesreq,
        "bodyfat": bodyfat,
        "bodyfat_source": bodyfat_source,
    })


@csrf_exempt
@require_POST
def api_chatbot(request):
    data = _parse_json_body(request)
    if not data:
        return JsonResponse({"ok": False, "message": "Invalid request"}, status=400)

    question = data.get("question", "").strip()
    if not question:
        return JsonResponse({"ok": False, "message": "Question is required"}, status=400)

    history = data.get("history", [])
    if not isinstance(history, list):
        history = []

    answer = chatfunction(question, history)
    return JsonResponse({"ok": True, "answer": answer})


@csrf_exempt
@require_POST
def api_save_diet(request):
    data = _parse_json_body(request)
    if not data:
        return JsonResponse({"ok": False, "message": "Invalid request payload"}, status=400)

    items = data.get("items", [])
    if not isinstance(items, list):
        return JsonResponse({"ok": False, "message": "Invalid selected items"}, status=400)

    _ensure_session_key(request)

    selected_calories = int(data.get("selected_calories", 0) or 0)
    target_calories = int(data.get("target_calories", 0) or 0)
    period = _normalize_period(data.get("period"))
    plan_date = _parse_plan_date(data.get("plan_date"))
    multiplier = _period_days(period, plan_date)
    selected_calories = selected_calories * multiplier
    target_calories = target_calories * multiplier

    saved = SavedDiet.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key,
        period=period,
        plan_date=plan_date,
        target_calories=target_calories,
        selected_calories=selected_calories,
        selected_items=json.dumps(items),
        bmi=float(data.get("bmi")) if data.get("bmi") not in (None, "") else None,
        bodyfat=float(data.get("bodyfat")) if data.get("bodyfat") not in (None, "") else None,
        bmiinfo=str(data.get("bmiinfo") or ""),
    )

    return JsonResponse({"ok": True, "message": "Diet saved successfully", "saved_id": saved.id})


@require_GET
def api_diet_history(request):
    owner_filter = _owner_lookup(request)
    saved_diets = SavedDiet.objects.filter(**owner_filter)

    history = []
    for record in saved_diets:
        try:
            items = json.loads(record.selected_items)
        except json.JSONDecodeError:
            items = []
        history.append({
            "id": record.id,
            "created_at": record.created_at.isoformat(),
            "plan_date": (record.plan_date.isoformat() if record.plan_date else None),
            "period": record.period,
            "selected_calories": record.selected_calories,
            "target_calories": record.target_calories,
            "bmi": record.bmi,
            "bodyfat": record.bodyfat,
            "bmiinfo": record.bmiinfo,
            "items": items,
        })

    return JsonResponse({"ok": True, "history": history})


@require_GET
def api_diet_tracker(request):
    period = _normalize_period(request.GET.get("period"))

    owner_filter = _owner_lookup(request)
    saved_diets = SavedDiet.objects.filter(period=period, **owner_filter)

    buckets = {}
    for record in saved_diets:
        plan_date = _record_plan_date(record)

        if period == "weekly":
            iso_year, iso_week, _ = plan_date.isocalendar()
            key = f"{iso_year}-W{iso_week:02d}"
            start = plan_date - timedelta(days=plan_date.weekday())
        elif period == "monthly":
            key = f"{plan_date.year}-{plan_date.month:02d}"
            start = plan_date.replace(day=1)
        else:
            key = plan_date.isoformat()
            start = plan_date

        entry = buckets.setdefault(key, {
            "key": key,
            "start_date": start.isoformat(),
            "records": 0,
            "selected_calories": 0,
            "target_calories": 0,
        })
        entry["records"] += 1
        entry["selected_calories"] += record.selected_calories
        entry["target_calories"] += record.target_calories

    summary = sorted(buckets.values(), key=lambda b: b["start_date"])
    return JsonResponse({"ok": True, "period": period, "summary": summary})


@require_GET
def api_preferences(request):
    owner_filter = _owner_lookup(request)
    pref = UserPreference.objects.filter(**owner_filter).first()
    if not pref:
        return JsonResponse({"ok": True, "preferences": None})
    return JsonResponse({
        "ok": True,
        "preferences": {
            "age": pref.age,
            "weight": pref.weight,
            "height": pref.height,
            "bodyfat": pref.bodyfat,
            "goal": pref.goal,
            "activity": pref.activity,
            "gender": pref.gender,
            "category": pref.category,
            "plan_period": pref.plan_period,
            "plan_date": pref.plan_date.isoformat() if pref.plan_date else None,
            "reminder_time": pref.reminder_time,
        }
    })


@csrf_exempt
@require_POST
def api_save_preferences(request):
    data = _parse_json_body(request)
    if not data:
        return JsonResponse({"ok": False, "message": "Invalid request"}, status=400)

    owner_filter = _owner_lookup(request)
    pref = UserPreference.objects.filter(**owner_filter).first()
    if not pref:
        pref = UserPreference(**_owner_create(request))

    pref.age = _parse_int(data.get("age"))
    pref.weight = _parse_int(data.get("weight"))
    pref.height = _parse_int(data.get("height"))
    pref.bodyfat = _parse_float(data.get("bodyfat"))
    pref.goal = data.get("goal") or pref.goal
    pref.activity = data.get("activity") or pref.activity
    pref.gender = data.get("gender") or pref.gender
    pref.category = data.get("category") or pref.category
    if "plan_period" in data:
        pref.plan_period = _normalize_period(data.get("plan_period"))
    if "plan_date" in data:
        pref.plan_date = _parse_plan_date(data.get("plan_date"))
    if "reminder_time" in data:
        pref.reminder_time = (data.get("reminder_time") or "").strip()
    pref.save()

    return JsonResponse({"ok": True})


@require_GET
def api_favorites(request):
    owner_filter = _owner_lookup(request)
    favorites = FavoriteFood.objects.filter(**owner_filter).select_related("food")
    items = [
        {
            "id": fav.id,
            "food_id": fav.food.id,
            "name": fav.food.name,
            "cal": fav.food.cal,
            "fat": fav.food.fat,
            "pro": fav.food.pro,
            "sug": fav.food.sug,
            "imagepath": fav.food.imagepath,
        }
        for fav in favorites
    ]
    return JsonResponse({"ok": True, "favorites": items})


@csrf_exempt
@require_POST
def api_toggle_favorite(request):
    data = _parse_json_body(request)
    if not data:
        return JsonResponse({"ok": False, "message": "Invalid request"}, status=400)

    food_id = data.get("food_id")
    action = (data.get("action") or "toggle").strip().lower()
    if not food_id:
        return JsonResponse({"ok": False, "message": "food_id is required"}, status=400)

    owner_filter = _owner_lookup(request)
    try:
        food = Food.objects.get(pk=food_id)
    except Food.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Food not found"}, status=404)

    existing = FavoriteFood.objects.filter(food=food, **owner_filter).first()
    if action == "add":
        if not existing:
            FavoriteFood.objects.create(food=food, **_owner_create(request))
        return JsonResponse({"ok": True, "favorite": True})
    if action == "remove":
        if existing:
            existing.delete()
        return JsonResponse({"ok": True, "favorite": False})

    if existing:
        existing.delete()
        return JsonResponse({"ok": True, "favorite": False})
    FavoriteFood.objects.create(food=food, **_owner_create(request))
    return JsonResponse({"ok": True, "favorite": True})


@require_GET
def api_water_status(request):
    owner_filter = _owner_lookup(request)
    today = timezone.localdate()
    log = WaterLog.objects.filter(log_date=today, **owner_filter).first()
    amount = log.amount_ml if log else 0

    recent = WaterLog.objects.filter(**owner_filter).order_by("-log_date")[:7]
    history = [
        {"date": r.log_date.isoformat(), "amount_ml": r.amount_ml}
        for r in reversed(recent)
    ]

    return JsonResponse({"ok": True, "today": {"date": today.isoformat(), "amount_ml": amount}, "history": history})


@csrf_exempt
@require_POST
def api_water_update(request):
    data = _parse_json_body(request)
    if not data:
        return JsonResponse({"ok": False, "message": "Invalid request"}, status=400)

    owner_filter = _owner_lookup(request)
    log_date = _parse_plan_date(data.get("date"))
    amount_ml = data.get("amount_ml")
    delta_ml = data.get("delta_ml")

    log = WaterLog.objects.filter(log_date=log_date, **owner_filter).first()
    if not log:
        log = WaterLog(log_date=log_date, amount_ml=0, **_owner_create(request))

    if amount_ml is not None:
        log.amount_ml = int(amount_ml)
    elif delta_ml is not None:
        log.amount_ml = max(0, log.amount_ml + int(delta_ml))

    log.save()
    return JsonResponse({"ok": True, "date": log_date.isoformat(), "amount_ml": log.amount_ml})


@require_GET
def api_diet_insights(request):
    owner_filter = _owner_lookup(request)
    saved_list = SavedDiet.objects.filter(**owner_filter).order_by('-created_at')
    plan_dates = sorted({ _record_plan_date(r) for r in saved_list })
    total_plans = len(saved_list)

    streak = 0
    longest = 0
    current = 0
    prev = None
    for d in plan_dates:
        if prev and (d - prev).days == 1:
            current += 1
        else:
            current = 1
        longest = max(longest, current)
        prev = d

    if plan_dates:
        last = plan_dates[-1]
        if (timezone.localdate() - last).days in (0, 1):
            streak = current

    # Calculate average adherence
    avg_adherence = 0.0
    if total_plans > 0:
        total_adherence = 0
        for record in saved_list:
            if record.target_calories > 0:
                adherence = (record.selected_calories / record.target_calories) * 100
                adherence = min(adherence, 200)  # Cap at 200%
                total_adherence += adherence
        avg_adherence = round(total_adherence / total_plans, 1)

    # Get 7-day weekly trend
    today = timezone.localdate()
    weekly_trend = []
    for i in range(6, -1, -1):  # Last 7 days
        date = today - timedelta(days=i)
        day_records = saved_list.filter(created_at__date=date)
        if day_records.exists():
            total_cal = sum(r.selected_calories for r in day_records)
            target_cal = sum(r.target_calories for r in day_records)
            weekly_trend.append({
                "date": date.isoformat(),
                "cal": total_cal,
                "target": target_cal,
                "adherence": round((total_cal / target_cal * 100), 1) if target_cal > 0 else 0
            })
        else:
            weekly_trend.append({
                "date": date.isoformat(),
                "cal": 0,
                "target": 0,
                "adherence": 0
            })

    # Get recent diets (last 5)
    recent_diets = []
    for record in saved_list[:5]:
        recent_diets.append({
            "id": record.id,
            "created_at": record.created_at.isoformat(),
            "plan_date": record.plan_date.isoformat() if record.plan_date else None,
            "period": record.period,
            "selected_calories": record.selected_calories,
            "target_calories": record.target_calories,
            "bmi": record.bmi,
            "bodyfat": record.bodyfat,
        })

    # Stats
    most_selected_food = "—"
    preferred_time = "lunch"
    if total_plans > 0:
        # Find most selected food
        all_foods = []
        for record in saved_list:
            try:
                items = json.loads(record.selected_items or '[]')
                all_foods.extend([item.get('name', '') for item in items])
            except:
                pass
        if all_foods:
            counter = Counter(all_foods)
            most_selected_food = counter.most_common(1)[0][0] if counter else "—"

    badges = []
    if total_plans >= 1:
        badges.append({"title": "First Plan", "detail": "Saved your first diet plan"})
    if total_plans >= 5:
        badges.append({"title": "Consistent", "detail": "Saved 5 diet plans"})
    if longest >= 7:
        badges.append({"title": "7-Day Streak", "detail": "Planned 7 days in a row"})

    return JsonResponse({
        "ok": True,
        "streak_days": streak,
        "total_diets": total_plans,
        "avg_calorie_adherence": avg_adherence,
        "stats": {
            "most_selected_food": most_selected_food,
            "preferred_time": preferred_time,
            "longest_streak": longest,
        },
        "weekly_trend": weekly_trend,
        "recent_diets": recent_diets,
        "badges": badges,
    })


@require_GET
def api_user_profile(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "message": "Not authenticated"}, status=401)
    return JsonResponse({
        "ok": True,
        "user": {
            "username": request.user.username,
            "email": request.user.email,
            "date_joined": request.user.date_joined.isoformat(),
        }
    })


@csrf_exempt
def api_delete_diet(request, pk):
    if request.method != "DELETE":
        return JsonResponse({"ok": False, "message": "Method not allowed"}, status=405)
    try:
        record = SavedDiet.objects.get(pk=pk)
    except SavedDiet.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Not found"}, status=404)

    if request.user.is_authenticated:
        if record.user != request.user:
            return JsonResponse({"ok": False, "message": "Not authorised"}, status=403)
    else:
        session_key = request.session.session_key
        if record.session_key != session_key:
            return JsonResponse({"ok": False, "message": "Not authorised"}, status=403)

    record.delete()
    return JsonResponse({"ok": True})
