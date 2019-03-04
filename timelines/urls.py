# from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='timelines/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='timelines/logout.html'), name='logout'),

    path('', views.home, name="home"),

    path('<int:campaignid>', views.campaign, name="campaign"),
    path('<str:campaigntype>/<int:campaignid>', views.campaign_type, name="campaign-types"),

    path('edit/week', views.edit_week, name="edit-week"),
    path('edit/campaign', views.edit_campaign, name="edit-campaign"),
    path('edit/campaign/info', views.edit_campaign_info, name="edit-campaign-info"),
    path('edit/task', views.edit_task, name="edit-task"),
    path('edit/task/version', views.edit_task_version, name="edit-task-version"),
    path('edit/comment', views.edit_comment, name="edit-comment"),
    path('edit/task/comment', views.edit_task_comment, name="edit-task-comment"),
    path('edit/task/version', views.edit_task_version, name="edit-task-version"),
    path('edit/link', views.edit_link, name="edit-link"),
    path('save/comment', views.save_comment, name="save-comment"),
    path('save/link', views.save_link, name="save-link"),
    path('clone', views.clone, name="clone"),

    path('save/campaign', views.save_campaign, name="save-campaign"),
    path('save/campaign/info', views.save_campaign_info, name="save-campaign-info"),
    path('save/campaign/capacity', views.save_campaign_capacity, name="save-campaign-capacity"),
    path('save/campaign/quantifiers', views.save_campaign_quantifiers, name="save-campaign-quantifiers"),
    path('save/campaign/link', views.save_campaign_link, name="save-campaign-link"),
    path('save/week', views.save_week, name="save-week"),

    path('save/task', views.save_task, name="save-task"),
    path('save/task/adjust', views.save_task_adjust, name="save-task-adjust"),
    path('save/task/version', views.save_task_version, name="save-task-version"),
    path('delete', views.delete, name="delete"),
    path('cancel', views.cancel, name="cancel"),

    path('pax', views.pax, name="pax"),
    path('dax', views.dax, name="dax"),
    path('food', views.food, name="food"),
    path('financial', views.financial, name="financial"),
    path('ventures', views.ventures, name="ventures"),

    path('new', views.new, name="new"),
    path('migration', views.migration, name="migration"),
    path('troubleshooting', views.troubleshooting, name="troubleshooting"),
    path('template', views.template, name="template"),

    path('ru', views.ru_report, name="ru-report"),
    path('tasks', views.tasks_report, name="tasks-report"),

    path('analytics', views.analytics, name="ops-analytics"),
]
