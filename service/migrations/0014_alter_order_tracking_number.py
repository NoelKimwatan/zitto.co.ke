# Generated by Django 3.2.5 on 2022-02-11 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0013_ordertimeline_arrived_at_us_sort_facility'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(blank=True, max_length=250, null=True, unique=True),
        ),
    ]