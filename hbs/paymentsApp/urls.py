# payments/urls.py

from django.urls import path
from .views import deactivate_account,create_stripe_payment_intent, create_mpesa_payment_intent, mpesa_callback, refund_payment, Stripe_complete_payment, mpesa_b2c_result, mpesa_b2c_timeout

urlpatterns = [
    path('stripe/create/', create_stripe_payment_intent, name='create-stripe-payment-intent'),
    path('stripe/complete/', Stripe_complete_payment, name='Stripe_complete_payment'),
    path('mpesa/create/', create_mpesa_payment_intent, name='create-mpesa-payment-intent'),
    path('mpesa/timeout/', mpesa_b2c_timeout, name='mpesa-b2c-timeout'),
    path('result/', mpesa_b2c_result, name='mpesa-b2c-result'),
    path('callback/', mpesa_callback, name='mpesa-callback'),
    path('refund/', refund_payment, name='refund-payment'),
    path('deactivate/<uuid:user_id>/', deactivate_account, name='deactivate_account'),

]
