from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),

    path('workdays/', views.workdays, name='workdays'),

    path('workday/today', views.workday_today, name='workday_today'),
    path('workday/add_new', views.workday_add_new, name='workday_add_new'),

    path('workday/create/date=<_date>', views.workday_create, name='workday_create'),
    path('workday/edit/<int:workday_id>', views.workday_edit, name='workday_edit'),
    path('workday/delete/<int:workday_id>', views.workday_delete, name='workday_delete'),

    path('reports/', views.reports, name='reports'),

]
