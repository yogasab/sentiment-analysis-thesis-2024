from django.urls import path, re_path
from apps.sentiment_analysis import views

urlpatterns = [
    path('', views.index, name='index'),
    path('crawling', views.view_crawling, name='crawling'),
    path('crawling/search', views.search_crawling, name='crawling_search'),
    path('crawling/start', views.post_crawling_start, name='crawling_start'),
    path('sentiment-classification', views.view_sentiment_classification, name='sentiment_classification'),
    path('sentiment-classification/search', views.search_sentiment_classification, name='sentiment_classification'),
    path('insight', views.get_insight, name='insight'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
]
