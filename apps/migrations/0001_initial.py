# Generated by Django 5.1 on 2024-11-25 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_id', models.UUIDField()),
                ('username', models.CharField(max_length=255)),
                ('score', models.IntegerField()),
                ('created_at', models.DateTimeField()),
                ('content', models.TextField()),
                ('sentiment_content', models.CharField(max_length=50, null=True)),
            ],
            options={
                'db_table': 'application_review',
            },
        ),
    ]
