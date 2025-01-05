from django.urls import path, re_path
from apps.sentiment_analysis import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('crawling', views.view_crawling, name='crawling'),
    path('crawling/search', views.search_crawling, name='crawling_search'),
    path('crawling/start', views.post_crawling_start, name='crawling_start'),
    path('sentiment-classification', views.view_sentiment_classification, name='sentiment_classification'),
    path('sentiment-classification/search', views.search_sentiment_classification, name='sentiment_classification_search'),
    path('insight', views.get_insight, name='insight'),
    path('login', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page='/login'), name='logout'), 
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
]
