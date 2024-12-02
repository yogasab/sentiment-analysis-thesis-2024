import re
import time
import emoji
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import joblib
import os
from django.conf import settings
from googletrans import Translator
import pandas as pd
from google_play_scraper import app, Sort, reviews_all
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import string

nltk.download('punkt_tab')
nltk.download('stopwords')
class SentimentModel:
    def __init__(self):
        self.model = joblib.load(os.path.join(settings.BASE_DIR, 'sentiment_analysis_model', 'naive_bayes_model.pkl'))
        self.vectorizer = joblib.load(os.path.join(settings.BASE_DIR, 'sentiment_analysis_model', 'count_vectorizer.pkl'))
        self.translator = Translator()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def crawling_reviews(self, app_id):
        result = reviews_all(
            app_id,
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
        return my_df

    def preprocess_text(self, my_df: pd.DataFrame):
        processed_texts = []
        content_eng_list = []  
        for index, row in my_df.iterrows():
            text = row['content']  
            if not text or text.strip() == "":
                raise ValueError("Input text cannot be empty")
            text = text.replace(" g ", " gak ").replace(" y ", " ya ")
            text = emoji.demojize(text)
            try:
                time.sleep(0.3)  
                translated = self.translator.translate(text, src='auto', dest='en').text
                if not translated:  
                    raise ValueError("Translation returned empty result.")
            except Exception as e:
                print(f"Translation error: {e}")
                translated = text  
                
            translated = translated.lower()
            text = re.sub(r'[^\w\s]', '', translated)
            text = re.sub(r'(?<=\.)', ' ', text)
            text = text.replace("not ", "not_").replace("no ", "no_").replace("never ", "never_")\
                       .replace("cant ", "can not_").replace("can't ", "can not_").replace("out alone", "out_alone")
            content_eng_list.append(text)
            tokens = word_tokenize(text)
            filtered_words = [word for word in tokens if word not in self.stop_words]
            lemmatized_words = [self.lemmatizer.lemmatize(word) for word in filtered_words]
            processed_texts.append(' '.join(lemmatized_words))
        my_df['content_eng'] = content_eng_list
        return my_df, processed_texts 

    def predict_sentiment(self, my_df: pd.DataFrame):
        my_df, processed_texts = self.preprocess_text(my_df)
        processed_texts_vectorized = self.vectorizer.transform(processed_texts)
        predictions = self.model.predict(processed_texts_vectorized)
        sentiments = ["Positive" if pred == 1 else "Negative" for pred in predictions]
        my_df['sentiment'] = sentiments 
        return my_df 

    def get_most_common_words(self, reviews_by_year):
        stop_words = set(stopwords.words('indonesian')) 
        stop_words.update(['ya', 'ga', 'iya', 'y', 'g', 'ngga', 'tdk', 'gak', 'tdak', 'nya', 'yg', 'tp', 'tpi', 'tapi', 'sih', 'si', 'nih', 'nihh'])
        result = []  
        for year_data in reviews_by_year:
            year = year_data['year']
            contents = year_data['content']
            sentiments = year_data['sentiments']
            positive_words = []
            negative_words = []
            for review, sentiment in zip(contents, sentiments):
                words = word_tokenize(review.lower()) 
                words_cleaned = [
                    word for word in words
                    if word not in stop_words and word not in string.punctuation
                ]
                if sentiment == 'Positive':
                    positive_words.extend(words_cleaned)
                elif sentiment == 'Negative':
                    negative_words.extend(words_cleaned)
            positive_word_counts = Counter(positive_words)
            negative_word_counts = Counter(negative_words)
            most_common_positive = positive_word_counts.most_common(4)
            most_common_negative = negative_word_counts.most_common(4)
            result.append({
                'year': year,
                'most_common_positive': most_common_positive,
                'most_common_negative': most_common_negative
            })
        return result

