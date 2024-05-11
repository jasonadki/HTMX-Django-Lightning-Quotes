from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from uuid import uuid4

from .models import Quote

from payments.models import Payment
from payments.views import InvoiceGenerator




def dashboard(request):
    # Get all quotes for the current user if they are authenticated
    if not request.user.is_authenticated:
        return render(request, 'quotes/dashboard.html', {'quotes': []})
    else:
        quotes = Quote.objects.filter(user=request.user)
        return render(request, 'quotes/dashboard.html', {'quotes': quotes})




def generate_qr_code_html(payment_address):
    # Generate the QR code HTML
    qr_code_html = f'<img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={payment_address}" alt="QR Code">'
    # Return a tuple with the QR code HTML and the LN address
    return qr_code_html, payment_address


def add_quote(request):
    
    if 'user_token' not in request.session:
        request.session['user_token'] = str(uuid4())


    session_token = request.session['user_token']  # Retrieve the session token

    anonymous_review = False

    # Check if user is authenticated or if anonymous review
    if not request.user.is_authenticated:
        anonymous_review = True

    # If not anonymous review, create a review with a user
    if not anonymous_review:
        if request.method == 'POST':
            # Extract review data from form submission
            content = request.POST.get('content')
            btc_amount = request.POST.get('integer_field')  # Amount in Satoshis the user agrees to pay

            # Initialize the invoice generator
            invoice_generator = InvoiceGenerator()
            description = f"Payment for review by Jason"

            # Create a payment invoice
            payment_address, invoice_id = invoice_generator.create_invoice(btc_amount, content, description)


            if invoice_id:
                # Create and save the payment record
                payment = Payment.objects.create(
                    btc_payserver_invoice_id=invoice_id,
                    is_paid=False,
                    amount=btc_amount

                )

                # Save the review with the payment record attached, marking it as not valid initially
                quote = Quote.objects.create(
                    user=request.user,
                    content=content,
                    payment=payment,
                    session_token=session_token,
                )

                # Generate the QR code HTML
                qr_code_html, ln_address = generate_qr_code_html(payment_address)

                # Pass both the QR code HTML and LN address to your template
                html_snippet = render_to_string('partials/payment_info.html', {'qr_code_html': qr_code_html, 'ln_address': ln_address, 'quote': quote, 'btc_amount': btc_amount})

                return HttpResponse(html_snippet)
            else:
                return HttpResponse('Failed to create payment invoice.', status=500)
            
    else:
        # If anonymous review, create a review without a user
         if request.method == 'POST':
            # Extract review data from form submission
            content = request.POST.get('content')
            btc_amount = request.POST.get('integer_field')

            # Initialize the invoice generator
            invoice_generator = InvoiceGenerator()
            description = f"Payment for review by Jason"

            # Create a payment invoice
            payment_address, invoice_id = invoice_generator.create_invoice(btc_amount, content, description)

            if invoice_id:
                # Create and save the payment record
                payment = Payment.objects.create(
                    btc_payserver_invoice_id=invoice_id,
                    is_paid=False,
                    amount=btc_amount
                )

                quote = Quote.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    content=content,
                    payment=payment,
                    session_token=session_token,
                )

                
                qr_code_html, ln_address = generate_qr_code_html(payment_address)
                # Pass both the QR code HTML and LN address to your template
                html_snippet = render_to_string('partials/payment_info.html', {'qr_code_html': qr_code_html, 'ln_address': ln_address, 'quote': quote, 'btc_amount': btc_amount})

                return HttpResponse(html_snippet)
            else:
                return HttpResponse('Failed to create payment invoice.', status=500)


    # If not POST or failed to create an invoice, redirect back to the product detail page
    return redirect('dashboard')




@csrf_exempt  # Exempt this view from CSRF verification
def update_quote_status(request, quote_id):
    # Authentication check
    secret_token = request.headers.get('Authorization')
    if secret_token != "Bearer 123":
        return HttpResponse("Unauthorized", status=401)

    quote = get_object_or_404(Quote, id=quote_id)
    quote.status = 'Complete'
    quote.save()

    # Notify the user via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'quotes_{quote.user.id}',
        {
            "type": "quote.update",
            "quote_id": str(quote.id),
            "status": quote.status,
        }
    )

    return JsonResponse({'status': 'success', 'quote_id': str(quote.id), 'new_status': quote.status})
