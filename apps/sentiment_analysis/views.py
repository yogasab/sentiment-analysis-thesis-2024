from django import template
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from apps.sentiment_analysis.forms import SearchSentimentDataForm
from django.http import JsonResponse
import os
import pandas as pd
from django.conf import settings
from django.http import JsonResponse
from apps.models import ApplicationReview
from django.utils import timezone
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import SentimentModel
import json

def index(request):
    return HttpResponseRedirect("/crawling")

def view_crawling(request):
    application_reviews = ApplicationReview.objects.all()
    paginator = Paginator(application_reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    context = {
        'title': 'Crawling',
        'application_reviews': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'home/crawling.html', context)

def search_crawling(request):
    form = SearchSentimentDataForm(request.GET)
    application_reviews = None
    if form.is_valid():
        application_reviews = ApplicationReview.find_crawling_by_criteria(form)
    paginator = Paginator(application_reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': 'Crawling',
        'application_reviews': page_obj,
        'page_obj': page_obj,
        'search_keyword': request.GET.get('search_keyword'),
        'start_date': request.GET.get('start_date'),
        'end_date': request.GET.get('end_date'),
    }
    return render(request, 'home/crawling.html', context)

def post_crawling_start(request):
    if request.method == "POST":
        try:
            sentiment_model = SentimentModel()
            my_df = sentiment_model.crawling_reviews('com.opinia')
            if len(my_df) > 0:
                try:
                    file_path = os.path.join(settings.BASE_DIR, 'scrapped_data.csv')
                    my_df = pd.read_csv(file_path)
                    print("Predicting sentiment...")
                    my_df = sentiment_model.predict_sentiment(my_df)
                    print("Sentiment prediction done.")
                    my_df.to_csv(file_path, index=False)
                    print("Record data to database...")
                    ApplicationReview.process_application_review(my_df)
                    print("Record data to database done.")
                    return JsonResponse({
                        "status": "success",
                        "message": f"Proses crawling data selesai!"
                    })
                except Exception as e:
                    print("Exception : ", e)
                    return JsonResponse({
                        "status": "error",
                        "message": f"Terjadi kesalahan saat melakukan crawling: {str(e)}"
                    }, status=400)
            return JsonResponse({
                "status": "success",
                "message": f"Proses crawling data selesai!"
            })
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Terjadi kesalahan saat melakukan crawling: {str(e)}"
            }, status=400)

    else:
        return JsonResponse({
            "status": "error",
            "message": "Metode permintaan tidak valid!"
        }, status=405)

def search_sentiment_classification(request):
    form = SearchSentimentDataForm(request.GET)
    application_reviews = None
    if form.is_valid():
        application_reviews = ApplicationReview.find_crawling_by_criteria(form)
    paginator = Paginator(application_reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': 'Sentiment Classification',
        'application_reviews': page_obj,
        'page_obj': page_obj,
        'search_keyword': request.GET.get('search_keyword'),
        'start_date': request.GET.get('start_date'),
        'end_date': request.GET.get('end_date'),
    }
    return render(request, 'home/sentiment_classification.html', context)

def view_sentiment_classification(request):
    application_reviews = ApplicationReview.objects.all()
    paginator = Paginator(application_reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    context = {
        'title': 'Sentiment Classification',
        'application_reviews': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'home/sentiment_classification.html', context)

def get_insight(request):
    sentiment_model = SentimentModel()
    application_reviews = ApplicationReview.get_review_summary()
    application_reviews_by_year = sentiment_model.get_most_common_words(ApplicationReview.get_review_summary_by_year())
    application_reviews_data = {}
    for review in application_reviews:
        year = review['year']
        if year not in application_reviews_data:
            application_reviews_data[year] = {'positive': 0, 'negative': 0}
        sentiment = review['sentiment_content'].lower()
        if sentiment == 'positive':
            application_reviews_data[year]['positive'] += review['record_count']
        elif sentiment == 'negative':
            application_reviews_data[year]['negative'] += review['record_count']
    combined_data = {}
    for review in application_reviews_by_year:
        year = review['year']
        most_common_positive = review['most_common_positive']
        most_common_negative = review['most_common_negative']
        if year not in combined_data:
            combined_data[year] = {
                'positive': 0,  
                'negative': 0,  
                'most_common_positive': [],  
                'most_common_negative': []
            }
        combined_data[year]['most_common_positive'] = most_common_positive
        combined_data[year]['most_common_negative'] = most_common_negative
        if year in application_reviews_data:
            combined_data[year]['positive'] = application_reviews_data[year]['positive']
            combined_data[year]['negative'] = application_reviews_data[year]['negative']
    context = {
        'title': 'Insight',
        'application_reviews_data': json.dumps(combined_data),
        'labels': json.dumps(['Positive', 'Negative']),
    }
    html_template = loader.get_template('home/insight.html')
    return HttpResponse(html_template.render(context, request))

def pages(request):
    context = {}
    try:
        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
