from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

import requests
import json
import hmac
import hashlib

from .models import Payment

from quotes.models import Quote

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



from QuoteFlowApp.settings import (
    VOLTAGE_KEY,
    VOLTAGE_STORE_ID,
    PAYMENT_WEBHOOK_SECRET,
    API_BEARER_TOKEN
)



class InvoiceGenerator:
    def __init__(self, storeID = VOLTAGE_STORE_ID):
        self.base_url = "https://btcpay0.voltageapp.io/api/v1/stores"
        self.storeID = storeID
        self.invoice_base_url = f"{self.base_url}/{self.storeID}/invoices"
        self.auth_token = f"token {VOLTAGE_KEY}"  

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": self.auth_token
        }

    def create_invoice(self, btc_amount, orderId, description="empty description"):
        invoice_data = {
            "description": description,
            "amount": btc_amount,
            # "expiry": 3600
            "currency": "SATS",
            "metadata": {
                "itemDesc": description,
                'orderId': orderId
            }
        }

        

        response = requests.post(self.invoice_base_url, json=invoice_data, headers=self.headers)

        if response.status_code == 200:
            invoice_response = response.json()
            invoice_id = invoice_response['id']

            # URL
            self.payment_method_url = f"{self.base_url}/{self.storeID}/invoices/{invoice_id}/payment-methods"

            payment_method_response = requests.get(self.payment_method_url, headers=self.headers)

            # If the payment method is LN, return the LN address
            if payment_method_response.status_code == 200:
                payment_method_data = payment_method_response.json()

                for payment_method in payment_method_data:
                    if 'destination' in payment_method:
                        if payment_method['destination'] != None:
                            return payment_method['destination'], invoice_id

                return "No payment method with destination found."
            else:
                return f"Failed to get payment method, status code: {payment_method_response.status_code}"

        else:
            return f"Failed to create invoice, status code: {response.status_code}"




@csrf_exempt
def payment_webhook(request):
    if request.method == 'POST':
        payment_data = request.body
        payload = json.loads(request.body)
        
        btcpay_sig = request.headers.get('BTCPAY-SIG').split('=')[1]
        
        
        hmac_obj = hmac.new(PAYMENT_WEBHOOK_SECRET.encode(), payment_data, hashlib.sha256)
        calculated_sig = hmac_obj.hexdigest()
        
        if btcpay_sig == calculated_sig:
            if payload['type'] == 'InvoiceReceivedPayment':
                invoice_id = payload['invoiceId']
                try:
                    payment = Payment.objects.get(btc_payserver_invoice_id=invoice_id)
                    payment.is_paid = True
                    payment.save()
                                      
                    try:
                        quote = Quote.objects.get(payment=payment)
                        handle_quote_payment(quote)
                    except Quote.DoesNotExist:
                        return HttpResponse(status=404)
                        
                    return JsonResponse({'status': 'success', 'quote_id': str(quote.id), 'new_status': quote.is_valid})

                except Payment.DoesNotExist:
                    return HttpResponse(status=404)
                except Quote.DoesNotExist:
                    return HttpResponse(status=404)

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=403)



def handle_quote_payment(quote):
    # Handle the quote
    quote.is_valid = True
    quote.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'quotes_{quote.session_token}',
        {
            "type": "quote.update",
            "quote_id": str(quote.id),
            "status": quote.is_valid,
        }
    )
    return JsonResponse({'status': 'success', 'quote_id': str(quote.id), 'new_status': quote.is_valid})




@csrf_exempt  # Exempt this view from CSRF verification
def update_quote_status(request, invoice_id):
    ###########################################################################
    # THIS IS FOR TESTING PURPOSES ONLY FOR APPLICATIONS LIKE POSTMAN
    ###########################################################################
    
    # Authentication check
    secret_token = request.headers.get('Authorization')
    if secret_token != f"Bearer {API_BEARER_TOKEN}":
        return HttpResponse("Unauthorized", status=401)

    payment = Payment.objects.get(btc_payserver_invoice_id=invoice_id)
    payment.is_paid = True
    payment.save()
    
                    
    try:
        quote = Quote.objects.get(payment=payment)
        handle_quote_payment(quote)
    except Quote.DoesNotExist:
        return HttpResponse(status=404)
        
    return JsonResponse({'status': 'success', 'quote_id': str(quote.id), 'new_status': quote.is_valid})
        
        

