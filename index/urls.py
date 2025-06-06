from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views.med_center_group_views import add_med_center_group, edit_med_center_group, group_medical_centers
from .views import response_views
from .views.auth_views import get_med_centers

urlpatterns = [
    # Основные страницы
    path('', views.index, name="index"),
    path('home/', views.home_view, name="home"),
    path('login', views.login_view, name="login"),
    path('logout', views.logout_view, name="logout"),
    path('register', views.register, name="register"),
    path('get_med_centers', get_med_centers, name='get_med_centers'),

    # Управление пользователями
    path('user-list/', views.user_list, name='user_list'),
    path('delete-users/', views.delete_users, name='delete_users'),
    path('user/<int:pk>/', views.user_detail, name='user_detail'),
    path('update_user_status/<int:user_id>/', views.update_user_status, name='update_user_status'),

    # Профиль пользователя
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change_profile_image/', views.change_profile_image, name='change_profile_image'),
    path('delete_profile_image/', views.delete_profile_image, name='delete_profile_image'),
    path('change-username/', views.change_username, name='change_username'),
    path('change-email/', views.change_email, name='change_email'),
    path('change-gender/', views.change_gender, name='change_gender'),
    path('change_date_of_birth/', views.change_date_of_birth, name='change_date_of_birth'),
    path('delete_date_of_birth/', views.delete_date_of_birth, name='delete_date_of_birth'),
    path('change_desc/', views.change_desc, name='change_desc'),

    # Управление формами
    path('form/list', views.form_list_view, name="form_list"),
    path('form/create', views.create_form, name="create_form"),
    
    # Шаблоны форм
    path('form/create/contact', views.contact_form_template, name="contact_form_template"),
    path('form/create/feedback', views.customer_feedback_template, name="customer_feedback_template"),
    path('form/create/event', views.event_registration_template, name="event_registration_template"),
    path('form/create/survey', views.social_survey_template, name="social_survey_template"),

    # Редактирование форм
    path('form/<str:code>/edit', views.edit_form, name="edit_form"),
    path('form/<str:code>/edit_title', views.edit_title, name="edit_title"),
    path('form/<str:code>/edit_description', views.edit_description, name="edit_description"),
    path('form/<str:code>/edit_background_color', views.edit_bg_color, name="edit_background_color"),
    path('form/<str:code>/edit_text_color', views.edit_text_color, name="edit_text_color"),
    path('form/<str:code>/edit_setting', views.edit_setting, name="edit_setting"),
    path('form/<str:code>/delete', views.delete_form, name="delete_form"),

    # Управление вопросами и вариантами ответов
    path('form/<str:code>/edit_question', views.edit_question, name="edit_question"),
    path('form/<str:code>/edit_choice', views.edit_choice, name="edit_choice"),
    path('form/<str:code>/add_choice', views.add_choice, name="add_choice"),
    path('form/<str:code>/remove_choice', views.remove_choice, name="remove_choice"),
    path('form/<str:code>/get_choice/<str:question>', views.get_choice, name="get_choice"),
    path('form/<str:code>/add_question', views.add_question, name="add_question"),
    path('form/<str:code>/delete_question/<str:question>', views.delete_question, name="delete_question"),
    path('form/<str:code>/copy_question/<int:question>', views.copy_question, name='copy_question'),
    path('update_question_order/<str:code>/', views.update_question_order, name='update_question_order'),
    path('update_max_value/<int:question_id>/', views.update_max_value, name='update_max_value'),
    path('check_question_has_answers/<int:question_id>/', views.check_question_has_answers, name='check_question_has_answers'),

    # Оценки и ответы
    # path('form/<str:code>/score', views.score, name="score"),
    # path('form/<str:code>/edit_score', views.edit_score, name="edit_score"),
    # path('form/<str:code>/answer_key', views.answer_key, name="answer_key"),
    # path('form/<str:code>/feedback', views.feedback, name="feedback"),
    # path('update-score/', views.update_score, name='update_score'),

    # Просмотр и настройка форм
    path('form/<str:code>/viewform', views.view_form, name="view_form"),
    path('form/<str:code>/colors', views.form_colors, name="form_colors"),
    path('form/<str:code>/share', views.form_share, name="form_share"),
    path('form/<str:code>/settings', views.form_settings, name="form_settings"),
    path('form/<str:code>/submit', views.submit_form, name="submit_form"),

    # Управление ответами
    path('form/<str:code>/responses', views.responses, name='responses'),
    path('form/<str:code>/response/<str:response_code>', views.response, name="response"),
    path('form/<str:code>/response/<str:response_code>/edit', views.edit_response, name="edit_response"),
    path('form/<str:code>/responses/delete', views.delete_responses, name="delete_responses"),
    path('delete_selected_responses/', views.delete_selected_responses, name='delete_selected_responses'),

    # Экспорт данных
    path('form/<str:code>/export_csv', views.exportcsv,name='export_csv'),
    path('form/<str:code>/responses/export_excel/', response_views.export_responses_to_excel, name='export_responses_to_excel'),
    path('form/<str:code>/responses/export_combined/', response_views.export_combined_excel, name='export_combined_excel'),
    path('form/<str:code>/responses/export_final_scores/', response_views.export_final_scores, name='export_final_scores'),

    # Управление медицинскими центрами
    path('manage-medical-centers/', views.manage_medical_centers, name='manage_medical_centers'),
    path('add-medical-center/', views.add_medical_center, name='add_medical_center'),
    path('edit-medical-center/<int:center_id>/', views.edit_medical_center, name='edit_medical_center'),
    path('update-med-center/<int:user_id>/', views.update_med_center, name='update_med_center'),

    # Группы медицинских центров
    path('add-med-center-group/', add_med_center_group, name='add_med_center_group'),
    path('edit-med-center-group/<int:group_id>/', edit_med_center_group, name='edit_med_center_group'),
    path('group-medical-centers/<int:group_id>/', group_medical_centers, name='group_medical_centers'),

    # API для загрузки данных
    path('form/<str:code>/responses/load', response_views.load_responses, name='load_responses'),
    path('form/<str:code>/responses/search', response_views.search_responses, name='search_responses'),
    path('form/<str:code>/responses/load_table', response_views.load_table_data, name='load_table_data'),
    path('form/<str:code>/responses/load_med_centers', response_views.load_med_centers_data, name='load_med_centers_data'),
    path('form/<str:code>/responses/load_total_scores', response_views.load_total_scores_data, name='load_total_scores_data'),
    path('form/<str:code>/responses/load_final_scores_chart', response_views.load_final_scores_chart_data, name='load_final_scores_chart'),
    path('form/<str:code>/responses/load_negative_impact_chart', response_views.load_negative_impact_chart_data, name='load_negative_impact_chart'),
    path("form/<str:code>/responses/analytics-data/", response_views.load_analytics_data, name="load_analytics_data"),

    # Сброс пароля
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name ='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name ='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name ='password_reset_complete'),

    # Страницы ошибок
    path('403', views.FourZeroThree, name="403"),
    path('404', views.FourZeroFour, name="404"),
]

# Настройки для режима отладки
if settings.DEBUG:
    urlpatterns += [re_path(r'^.*/$', views.FourZeroFour)]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)