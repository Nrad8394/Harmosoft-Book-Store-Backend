# Generated by Django 5.0.7 on 2024-09-13 05:44

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('refund_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('refund_status', models.CharField(default='pending', max_length=20)),
                ('refund_reason', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('payment_method', models.CharField(max_length=50)),
                ('result_code', models.CharField(max_length=100)),
                ('result_desc', models.CharField(max_length=100)),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('refunded', 'Refunded'), ('incomplete', 'Incomplete'), ('paid', 'Paid')], default='pending', max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_id', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='order.order')),
            ],
        ),
    ]
