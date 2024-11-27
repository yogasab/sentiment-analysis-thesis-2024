from django import forms

class SearchSentimentDataForm(forms.Form):
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
    search_keyword = forms.CharField(required=False)
