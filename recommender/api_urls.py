from django.urls import path
from recommender import api_views

urlpatterns = [
    path('csrf/', api_views.csrf_token_view, name='api_csrf'),
    path('auth/status/', api_views.auth_status, name='api_auth_status'),
    path('login/', api_views.api_login, name='api_login'),
    path('signup/', api_views.api_signup, name='api_signup'),
    path('logout/', api_views.api_logout, name='api_logout'),
    path('recommend/', api_views.api_recommend, name='api_recommend'),
    path('chatbot/', api_views.api_chatbot, name='api_chatbot'),
    path('save-diet/', api_views.api_save_diet, name='api_save_diet'),
    path('diet-history/', api_views.api_diet_history, name='api_diet_history'),
    path('diet-tracker/', api_views.api_diet_tracker, name='api_diet_tracker'),
    path('diet-history/<int:pk>/delete/', api_views.api_delete_diet, name='api_delete_diet'),
    path('preferences/', api_views.api_preferences, name='api_preferences'),
    path('preferences/save/', api_views.api_save_preferences, name='api_save_preferences'),
    path('favorites/', api_views.api_favorites, name='api_favorites'),
    path('favorites/toggle/', api_views.api_toggle_favorite, name='api_toggle_favorite'),
    path('water/', api_views.api_water_status, name='api_water_status'),
    path('water/update/', api_views.api_water_update, name='api_water_update'),
    path('diet-insights/', api_views.api_diet_insights, name='api_diet_insights'),
    path('user/profile/', api_views.api_user_profile, name='api_user_profile'),
]
