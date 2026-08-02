from django.urls import path
from . import views


urlpatterns = [

    path('', views.LSpage, name='LSpage'),

    path('login/', views.loginpage, name='loginpage'),

    path('signup/', views.signup, name='signup'),

    path('forgotpassword/', views.forgot_password, name='forgot_password'),

    path('dsb/', views.DSBord, name='DSBord'),

    path('CreateBtn/', views.create_project, name='CreateNewPage'),

    path('calendar/', views.calender, name="calendarpage"),


    
    path('profile/',views.profile,name="profile"),
    
    path('Notification/',views.notification,name="notification"),
    path('Project/',views.project,name="project"),
    path('project/status/<int:project_id>/<str:status>/', views.update_status, name='update_status'),
    path('project/delete/<int:id>/', views.delete_project, name='delete_project'),
    
    path('project/<int:id>/', views.project_detail, name='project_detail'),
    path('edit-project/<int:id>/', views.edit_project, name='edit_project'),
    path('update-status-dropdown/<int:id>/', views.update_status_dropdown, name='update_status_dropdown'),
    path('improve-description/', views.improve_description, name='improve_description'),
    path('delete-file/<int:id>/', views.delete_file, name='delete_file'),
    path('mark-read/<int:id>/', views.mark_read, name='mark_read'),
    path('add-event/', views.add_event, name='add_event'),
    path('delete-event/', views.delete_event, name='delete_event'),
    path('update-event/', views.update_event, name='update_event'),
    path('api/insights/', views.get_insights_api, name='get_insights_api'),


]

