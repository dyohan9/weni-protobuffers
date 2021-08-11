# Generated by Django 2.2.24 on 2021-08-03 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0032_merge_20210803_1911"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="payment_status",
            field=models.CharField(
                choices=[
                    ("pending", "pending"),
                    ("paid", "paid"),
                    ("canceled", "canceled"),
                    ("fraud", "fraud"),
                    ("disputed", "disputed"),
                ],
                default="pending",
                max_length=8,
                verbose_name="payment status",
            ),
        ),
    ]