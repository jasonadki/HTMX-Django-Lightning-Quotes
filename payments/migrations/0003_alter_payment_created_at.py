# Generated by Django 5.0.3 on 2024-05-11 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_alter_payment_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]