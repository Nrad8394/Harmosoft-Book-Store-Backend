# payments/views.py

import logging
from django.http import HttpResponse, JsonResponse
from django_daraja.mpesa.core import MpesaClient
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from .models import Payment, Refund
from order.models import Order
from .serializers import PaymentSerializer, RefundSerializer
import stripe
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction
from userManager.permissions import CustomUserPermission
from rest_framework.permissions import AllowAny
import pusher

stripe.api_key = 'sk_test_51PIagZRqEfocF1LO0AZzjSVaiW0LEsPEQvXBf9940iEJc363k78oNqNKZxtPjcD6CKiIqJrSEFEHPDx2VxQn6Umv00L3RsFJGZ'

logger = logging.getLogger('payments')
from django.shortcuts import get_object_or_404, redirect
from userManager.models import CustomUser
from django.http import HttpResponse
@api_view(['POST'])
def deactivate_account(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = False
    user.save()
    return HttpResponse("Your account has been deactivated.")
@api_view(['POST'])
def create_stripe_payment_intent(request):
    try:
        order_id = request.data.get('orderId')
        if not order_id:
            logger.error('orderId is required.')
            return Response({'error': 'orderId is required.'}, status=status.HTTP_400_BAD_REQUEST)
        order = Order.objects.get(id=order_id)

        payment_method = request.data.get('payment_method')
        if not payment_method:
            logger.error('Payment method is required.')
            return Response({'error': 'Payment method is required.'}, status=status.HTTP_400_BAD_REQUEST)

        intent = stripe.PaymentIntent.create(
            amount=int(order.total * 100),
            currency='usd',
            payment_method=payment_method,
            confirm=True,
            return_url = "https://api.harmosoftbookstore.co.ke/"
        )
        payment = Payment.objects.create(
            order=order,
            payment_method='stripe',
            payment_status='paid' if intent.status == 'succeeded' else 'pending',
            amount=order.total,
            transaction_id=intent.id
        )
        order.stripe_id = intent.id
        order.payment_status = 'paid' if intent.status == 'succeeded' else 'pending'
        order.save()
        logger.info(f'Payment created for order {order_id} with status {payment.payment_status}')
        return Response({'payment_details': PaymentSerializer(payment).data})
    except stripe.error.StripeError as e: # type: ignore
        logger.error(f'Stripe error: {str(e)}')
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def Stripe_complete_payment(request):
    payment_id = request.data.get('payment_id')
    if not payment_id:
        logger.error('payment_id is required.')
        return Response({'error': 'payment_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        intent = stripe.PaymentIntent.retrieve(payment_id)
        if intent.status == 'succeeded':
            order = Order.objects.get(stripe_id=intent.id)
            order.payment_status = "paid"
            order.save()
            logger.info(f'Payment completed for order {order.id}')
            return Response({'message': 'Payment successful! Order completed.'})
        else:
            logger.warning(f'Payment failed or still in progress for payment_id {payment_id}')
            return Response({'error': 'Payment failed or still in progress.'}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.StripeError as e: # type: ignore
        logger.error(f'Stripe error: {str(e)}')
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_mpesa_payment_intent(request):
    cl = MpesaClient()
    
    # Extract and validate request data
    order_id = request.data.get('orderId')
    phone_number = request.data.get('phone_number')
    
    if not order_id:
        logger.error('orderId is required.')
        return Response({'error': 'orderId is required.'}, status=status.HTTP_400_BAD_REQUEST)

    if not phone_number:
        logger.error('phone_number is required.')
        return Response({'error': 'phone_number is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch the order
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f'Order with id {order_id} does not exist.')
        return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

    account_reference = f'order-{order_id}'
    transaction_desc = f'Payment for Harmosoft BookStore order-{order_id}'
    callback_url = 'https://api.harmosoftbookstore.co.ke/api/callback/'
    amount = int(order.total)

    try:
        logger.info(f'Initiating MPESA payment for order {order_id} of amount {amount}.')
        response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
        response_data = response.json()  # Convert response to JSON
        
        # Check for successful response
        if response.status_code != 200:
            logger.error(f'MPESA STK push failed: {response_data}')
            return Response({'error': 'Failed to initiate payment. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create payment record
        user = request.user if request.user.is_authenticated else None
        payment = Payment.objects.create(
            user=user,
            order=order,
            payment_method='mpesa',
            payment_status='pending',
            amount=order.total,
            transaction_id=response_data.get('MerchantRequestID', '')
        )

        # Update order with merchant request ID
        order.merchant_request_id = response_data.get('MerchantRequestID', '')
        order.save()

        logger.info(f'MPESA payment initiated for order {order_id} with status {payment.payment_status}')
        return Response({'payment_details': PaymentSerializer(payment).data}, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f'MPESA error: {str(e)}')
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # Initialize Pusher
pusher_client = pusher.Pusher(
    key= 'f238dc2ebfb0118cdc08',
    secret= 'cc71326f6f4fdf574e84',
    app_id= '1763106',
    cluster= 'mt1',
    ssl=True
)

@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        try:
            if request.content_type != 'application/json':
                logger.warning('Invalid content type')
                return JsonResponse({'error': 'Invalid content type'}, status=400)

            body_unicode = request.body.decode('utf-8')
            logger.debug(f'Callback data received: {body_unicode}')
            data = json.loads(body_unicode)
            stk_callback = data.get('Body', {}).get('stkCallback', {})

            merchant_request_id = stk_callback.get('MerchantRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])

            logger.debug(f'MerchantRequestID: {merchant_request_id}, ResultCode: {result_code}, ResultDesc: {result_desc}')

            if not merchant_request_id:
                logger.error('Missing MerchantRequestID')
                return JsonResponse({'error': 'Missing MerchantRequestID'}, status=400)

            try:
                payment = Payment.objects.get(transaction_id=merchant_request_id)
                order = payment.order
            except Payment.DoesNotExist:
                logger.error('Payment not found.')
                return JsonResponse({'error': 'Payment not found'}, status=404)

            with transaction.atomic():
                if result_code == 0:
                    # Payment was successful
                    for item in callback_metadata:
                        logger.debug(f'Callback Metadata Item: {item}')
                        if item['Name'] == 'Amount':
                            payment.amount = item['Value']
                        elif item['Name'] == 'MpesaReceiptNumber':
                            order.mpesa_receipt_number = item['Value']
                    payment.payment_status = 'paid'
                    order.payment_status = 'paid'
                    order.amount_paid = payment.amount
                    # Send success message to the frontend via Pusher
                    pusher_client.trigger(f'order-{order.id}', 'transaction-status', {
                        'message': f'Transaction for order {order.id} was successful.',
                        'status': 'success',
                        'id': str(order.id)
                    })

                else:
                    # Payment failed or was cancelled
                    payment.payment_status = 'failed'
                    order.payment_status = 'failed'
                    payment.result_code = result_code
                    payment.result_desc = result_desc

                    # Send failure message to the frontend via Pusher
                    pusher_client.trigger(f'order-{order.id}', 'transaction-status', {
                        'message': f'Transaction for order {order.id} failed: {result_desc}.',
                        'status': 'failure',
                        'id': str(order.id)
                    })

                payment.save()
                order.save()

            logger.info(f'MPESA callback processed for order {order.id} with status {payment.payment_status}')
            return JsonResponse({'status': 'success'}, status=200)

        except json.JSONDecodeError:
            logger.error('Failed to decode JSON from request body')
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Payment.DoesNotExist:
            logger.error('Payment not found.')
            return JsonResponse({'error': 'Payment not found'}, status=404)
        except Exception as e:
            logger.error(f'MPESA callback error: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)
    else:
        logger.warning('Invalid request method')
        return JsonResponse({'error': 'Invalid request method'}, status=405)
# # views.py
# @permission_classes([AllowAny])
# @csrf_exempt
# def mpesa_callback(request):
#     if request.method == 'POST':
#         try:
#             if request.content_type != 'application/json':
#                 logger.warning('Invalid content type')
#                 return JsonResponse({'error': 'Invalid content type'}, status=400)

#             body_unicode = request.body.decode('utf-8')
#             logger.debug(f'Callback data received: {body_unicode}')
#             data = json.loads(body_unicode)
#             stk_callback = data.get('Body', {}).get('stkCallback', {})

#             merchant_request_id = stk_callback.get('MerchantRequestID')
#             result_code = stk_callback.get('ResultCode')
#             result_desc = stk_callback.get('ResultDesc')
#             callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])

#             logger.debug(f'MerchantRequestID: {merchant_request_id}, ResultCode: {result_code}, ResultDesc: {result_desc}')

#             if not merchant_request_id:
#                 logger.error('Missing MerchantRequestID')
#                 return JsonResponse({'error': 'Missing MerchantRequestID'}, status=400)

#             # Find the related order and payment
#             try:
#                 payment = Payment.objects.get(transaction_id=merchant_request_id)
#                 order = payment.order
#             except Payment.DoesNotExist:
#                 logger.error('Payment not found.')
#                 return JsonResponse({'error': 'Payment not found'}, status=404)

#             with transaction.atomic():
#                 if result_code == 0:
#                     # Payment was successful
#                     for item in callback_metadata:
#                         logger.debug(f'Callback Metadata Item: {item}')
#                         if item['Name'] == 'Amount':
#                             payment.amount = item['Value']
#                         elif item['Name'] == 'MpesaReceiptNumber':
#                             order.mpesa_receipt_number = item['Value']
#                     payment.payment_status = 'paid'
#                     order.payment_status = 'paid'

#                     # Send success message to the frontend for the specific order group
#                     channel_layer = get_channel_layer()
#                     async_to_sync(channel_layer.group_send)(
#                         f'transactions_{order.id}',  # Send to the order-specific group
#                         {
#                             'type': 'send_transaction_status',
#                             'message': f'Transaction for order {order.id} was successful.',
#                             'status': 'success',
#                             'id': order.id
#                         }
#                     )

#                 else:
#                     # Payment failed or was cancelled
#                     payment.payment_status = 'failed'
#                     order.payment_status = 'failed'
#                     payment.result_code = result_code
#                     payment.result_desc = result_desc

#                     # Send failure message to the frontend for the specific order group
#                     channel_layer = get_channel_layer()
#                     async_to_sync(channel_layer.group_send)(
#                         f'transactions_{order.id}',  # Send to the order-specific group
#                         {
#                             'type': 'send_transaction_status',
#                             'message': f'Transaction for order {order.id} failed: {result_desc}.',
#                             'status': 'failure',
#                             'id': order.id
#                         }
#                     )

#                 payment.save()
#                 order.save()

#             logger.info(f'MPESA callback processed for order {order.id} with status {payment.payment_status}')
#             return JsonResponse({'status': 'success'}, status=200)

#         except json.JSONDecodeError:
#             logger.error('Failed to decode JSON from request body')
#             return JsonResponse({'error': 'Invalid JSON'}, status=400)
#         except Payment.DoesNotExist:
#             logger.error('Payment not found.')
#             return JsonResponse({'error': 'Payment not found'}, status=404)
#         except Exception as e:
#             logger.error(f'MPESA callback error: {str(e)}')
#             return JsonResponse({'error': str(e)}, status=500)
#     else:
#         logger.warning('Invalid request method')
#         return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_classes([AllowAny])
@api_view(['POST'])
def refund_payment(request):
    payment_id = request.data.get('payment_id')
    if not payment_id:
        logger.error('payment_id is required.')
        return Response({'error': 'payment_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
    refund_amount = request.data.get('refund_amount', None)

    try:
        payment = Payment.objects.get(id=payment_id)
        order = payment.order

        if payment.payment_method == 'stripe' and refund_amount is not None:
            refund = stripe.Refund.create(
                payment_intent=payment.transaction_id,
                amount=int(refund_amount * 100)
            )
            refund_status = refund['status']
        elif payment.payment_method == 'mpesa':
            cl = MpesaClient()
            phone_number = request.data.get('phone_number')
            if not phone_number:
                logger.error('phone_number is required.')
                return Response({'error': 'phone_number is required.'}, status=status.HTTP_400_BAD_REQUEST)
            remarks = 'Refund for order ID {}'.format(order.id)
            occasion = 'Order Refund'
            response = cl.business_payment(phone_number, int(refund_amount) if refund_amount else int(payment.amount), remarks, 'https://api.harmosoftbookstore.co.ke/api/result/', occasion)
            response = response.json()
            refund_status = response.get('ResponseDescription', 'pending')

        Refund.objects.create(
            payment=payment,
            refund_amount=refund_amount if refund_amount else payment.amount,
            refund_status=refund_status,
            refund_reason=request.data.get('refund_reason', '')
        )

        payment.payment_status = 'refunded'
        order.payment_status = 'refunded'
        payment.save()
        order.save()

        logger.info(f'Refund initiated for payment {payment_id} with status {refund_status}')
        return Response({'message': 'Refund initiated', 'refund_status': refund_status})
    except Payment.DoesNotExist:
        logger.error('Payment not found.')
        return Response({'error': 'Payment not found'}, status=404)
    except Exception as e:
        logger.error(f'Refund error: {str(e)}')
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
@csrf_exempt
def mpesa_b2c_result(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            result = data.get('Result', {})
            result_code = result.get('ResultCode')
            result_desc = result.get('ResultDesc')
            transaction_id = result.get('TransactionID')
            phone_number = result.get('OriginatorConversationID')
            amount = result.get('Amount')

            # Update the refund status based on the result
            refund = Refund.objects.filter(payment__transaction_id=transaction_id).first()
            if refund:
                refund.refund_status = 'completed' if result_code == 0 else 'failed'
                refund.save()

            logger.info(f'MPESA B2C result processed with result code {result_code}')
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            logger.error(f'MPESA B2C result error: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)
    else:
        logger.warning('Invalid request method')
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_classes([AllowAny])
@csrf_exempt
def mpesa_b2c_timeout(request):
    logger.warning('MPESA B2C timeout received')
    return JsonResponse({'status': 'timeout received'}, status=200)
