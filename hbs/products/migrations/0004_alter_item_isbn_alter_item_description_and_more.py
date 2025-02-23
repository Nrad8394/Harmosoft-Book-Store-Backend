# Generated by Django 5.0.7 on 2024-09-16 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_item_isbn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='ISBN',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='description',
            field=models.TextField(blank=True, max_length=1500),
        ),
        migrations.AlterField(
            model_name='item',
            name='study_level',
            field=models.CharField(choices=[('All', 'ALL'), ('ECDE & Pre-Primary', 'ECDE & Pre-Primary'), ('Primary School', 'Primary School'), ('Junior Secondary', 'Junior School'), ('Secondary School', 'Secondary School'), ('Higher Education', 'Higher Education')], default='All', max_length=20),
        ),
    ]
