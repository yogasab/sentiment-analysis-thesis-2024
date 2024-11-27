from django import template
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from apps.sentiment_analysis.forms import SearchSentimentDataForm
from django.http import JsonResponse
from google_play_scraper import app, Sort, reviews_all
import os
import pandas as pd
import numpy as np
from django.conf import settings
from django.http import JsonResponse
from apps.models import ApplicationReview
from django.utils import timezone
from django.shortcuts import render
from django.core.paginator import Paginator

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
            result = reviews_all(
                'com.opinia',
                sleep_milliseconds=0, 
                lang='id',  
                country='id', 
                sort=Sort.NEWEST, 
            )
            df_crawling = pd.DataFrame(np.array(result), columns=['review'])
            df_crawling = df_crawling.join(pd.DataFrame(df_crawling.pop('review').tolist()))
            new_df = df_crawling[['reviewId', 'userName', 'score', 'at', 'content']]
            sorted_df_crawling = new_df.sort_values(by='at', ascending=False)
            my_df = sorted_df_crawling[['reviewId', 'userName', 'score', 'at', 'content']]
            if len(my_df) > 0:
                try:
                    ApplicationReview.process_application_review(my_df)
                    return JsonResponse({
                        "status": "success",
                        "message": f"Proses crawling data selesai!"
                    })
                except Exception as e:
                    return JsonResponse({
                        "status": "error",
                        "message": f"Terjadi kesalahan saat melakukan crawling: {str(e)}"
                    }, status=400)
            # Save to csv file
            # file_path = os.path.join(settings.BASE_DIR, 'scrapped_data.csv')
            # my_df.to_csv(file_path, index=False)
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
        'title': 'Crawling',
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
    context = {
        'title': 'Insight',
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
