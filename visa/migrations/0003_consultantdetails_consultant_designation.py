# Generated by Django 4.1.13 on 2024-01-24 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visa', '0002_consultantdetails_experience'),
    ]

    operations = [
        migrations.AddField(
            model_name='consultantdetails',
            name='consultant_designation',
            field=models.CharField(blank=True, max_length=60),
        ),
    ]