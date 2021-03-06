# Generated by Django 3.1.7 on 2021-03-28 06:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_auto_20210328_0455'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comlete',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='address',
            name='address_line1',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='country',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='first_name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='last_name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='phone_no',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='address',
            name='zipcode',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
