# Generated by Django 4.1.13 on 2024-09-22 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_datasheet_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasheet',
            name='sheet_name',
            field=models.CharField(choices=[('MACD', 'MACD'), ('Break', 'Break'), ('MA10', 'MA10'), ('MA20', 'MA20'), ('MA50', 'MA50')], max_length=50),
        ),
    ]
