from django.db import models
from django.utils import timezone
from pandas import DataFrame
import pandas as pd
from apps.sentiment_analysis.forms import SearchSentimentDataForm
from django.core.paginator import Paginator
from django.db.models import Q

# Create your models here.
class ApplicationReview(models.Model):
    review_id = models.UUIDField(name="review_id")
    username = models.CharField(max_length=255)
    score = models.IntegerField()
    created_at = models.DateTimeField(name="created_at")
    content = models.TextField()
    sentiment_content = models.CharField(max_length=50, name="sentiment_content", null=True)

    class Meta:
        db_table = 'application_review'

    def __str__(self):
        return self.username
    
    def process_application_review(my_df: DataFrame):
        try:
            ApplicationReview.objects.all().delete()
            for index, row in my_df.iterrows():
                created_at = pd.to_datetime(row['at'])
                if created_at.tzinfo is None:  # Check if it's naive
                    created_at = timezone.make_aware(created_at, timezone.get_current_timezone())
                application_review = ApplicationReview(
                    review_id=row['reviewId'],
                    username=row['userName'],
                    score=row['score'],
                    created_at=created_at,
                    content=row['content'],
                )
                application_review.save()  
        except Exception as e:
            return e

    def find_crawling_by_criteria(form: SearchSentimentDataForm):
        search_keyword = form.cleaned_data["search_keyword"]
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]

        queryset = ApplicationReview.objects.all()
        if search_keyword != "":
            queryset = queryset.filter(
                Q(username__icontains=search_keyword) | Q(content__icontains=search_keyword)
            )

        if start_date is not None and end_date is not None:
            queryset = queryset.filter(created_at__range=[start_date, end_date])
        elif start_date is not None:
            queryset = queryset.filter(created_at__gte=start_date)
        elif end_date is not None:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset.all()
