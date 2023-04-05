import json
import logging
import stripe
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from djstripe import webhooks
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from djstripe.models import Customer as CustomerDJStripe

from lianecare.courses.models import Course, Enrollment
from lianecare.orders.models import Order

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

User = get_user_model()


## SEZIONE VENDITA CORSI
@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


# @csrf_exempt
@login_required
@transaction.atomic
def create_payment_checkout_session(request):
    if request.method == 'POST':
        domain_url = 'https://' + request.get_host()
        stripe.api_key = settings.STRIPE_SECRET_KEY
        request_body = json.loads(request.body.decode('utf-8'))
        id_course = request_body.get('id_course')
        email_customer = request.user.email
        try:
            customer = CustomerDJStripe.objects.get(email=email_customer, livemode=settings.STRIPE_LIVE_MODE)
        except CustomerDJStripe.DoesNotExist:
            # Creo un nuovo utente con le API di Stripe
            stripe_new_customer = stripe.Customer.create(email=email_customer)
            # sincronizzo il nuovo utente con il db locale
            customer = CustomerDJStripe.sync_from_stripe_data(stripe_new_customer)
        except CustomerDJStripe.MultipleObjectsReturned:
            customer = CustomerDJStripe.objects.filter(email=email_customer)[0]
            logger.error("Ci sono più customer Stripe con la stessa email")
        try:
            course = Course.objects.get(id=id_course)
            checkout_session = stripe.checkout.Session.create(
                customer=customer.id,
                success_url=domain_url + '/ordini/corso/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + '/ordini/cancellato/',
                payment_method_types=['card'],
                mode='payment',
                #allow_promotion_codes=True,
                line_items=[
                    {
                        'price': course.price_stripe.id,
                        'quantity': 1,
                    },
                ],
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Course.DoesNotExist:
            logger.error("Stripe: Course doesn't exist!")
            return JsonResponse({'error': str("Si è verificato un errore riprova più tardi.")})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@login_required
def orderCourseSuccess(request):
    session_id = request.GET.get('session_id')
    user = request.user
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            payment_status = session.get('payment_status')
            if payment_status == 'paid':
                customer_stripe = session.get('customer')
                payment_intent = session.get('payment_intent')
                amount_total = session.get('amount_total')
                amount_subtotal = session.get('amount_subtotal')
                customer_email = session['customer_details']['email']

                line_items = stripe.checkout.Session.list_line_items(session_id, limit=1)
                if line_items['data']:
                    item = line_items['data'][0]
                    description = item.get('description')
                    product_stripe = item['price']['product']
                    price_stripe = item['price']['id']

                course = Course.objects.get(price_stripe__id=price_stripe)
                order, created = Order.objects.get_or_create(user=user,
                                                             session_stripe_id=session_id,
                                                             defaults={'payment_intent_stripe_id': payment_intent,
                                                                       'customer_stripe_id': customer_stripe,
                                                                       'price_stripe_id': price_stripe,
                                                                       'product_stripe_id': product_stripe,
                                                                       'product_description': description,
                                                                       'content_object': course,
                                                                       'amount_subtotal': amount_subtotal,
                                                                       'amount_total': amount_total
                                                                       })
                if created:
                    Enrollment.objects.create(user=user, course=course, order=order, session_stripe_id=session_id)

        except Course.DoesNotExist:
            logger.error("Stripe: Course doesn't exist!")
            messages.add_message(request, messages.ERROR, 'Qualcosa è andato storto, riprova più tardi o contattaci.')
        except Exception as e:
            logger.error('Mess errore: %s' % e)
            # logger.error('Tipo di eccezione: %s' % sys.exc_info()[0])
            # logger.error('Traceback: %s' % traceback.print_tb(sys.exc_info()[2]))
            messages.add_message(request, messages.ERROR, 'Qualcosa è andato storto, riprova più tardi o contattaci.')

        return render(request, template_name='orders/course-success.html',
                      context={'description': description})
    else:
        return redirect("home")


class CancelledView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/cancel.html'


#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context


# Stripe non invierà un csrf token!
@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    # una subscription con un free trial not involve an immediate payment ma genererà un altro webhook invoice.paid
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id')
        payment_status = session.get('payment_status')

        logger.info('Corso acquistato!')

        if payment_status == 'paid':
            customer_stripe = session.get('customer')
            payment_intent = session.get('payment_intent')
            amount_total = session.get('amount_total')
            amount_subtotal = session.get('amount_subtotal')
            customer_email = session['customer_details']['email']

            try:
                user = User.objects.get(email=customer_email)
                line_items = stripe.checkout.Session.list_line_items(session_id, limit=1)

                if line_items['data']:
                    item = line_items['data'][0]
                    description = item.get('description')
                    product_stripe = item['price']['product']
                    price_stripe = item['price']['id']

                course = Course.objects.get(price_stripe__id=price_stripe)
                order, created = Order.objects.get_or_create(user=user,
                                                             session_stripe_id=session_id,
                                                             defaults={'payment_intent_stripe_id': payment_intent,
                                                                       'customer_stripe_id': customer_stripe,
                                                                       'price_stripe_id': price_stripe,
                                                                       'product_stripe_id': product_stripe,
                                                                       'product_description': description,
                                                                       'content_object': course,
                                                                       'amount_subtotal': amount_subtotal,
                                                                       'amount_total': amount_total
                                                                       })
                if created:
                    Enrollment.objects.create(user=user, course=course, order=order, session_stripe_id=session_id)
            except User.DoesNotExist:
                logger.error("Stripe webhook: User doesn't exist!")
            except Course.DoesNotExist:
                logger.error("Stripe webhook: Course doesn't exist!")

        # TODO: send an email to the customer
        if event['type'] == 'checkout.session.async_payment_succeeded':
            pass

    return HttpResponse(status=200)


def do_something():
    pass  # send a mail, invalidate a cache, fire off a Celery task, etc.


@webhooks.handler("checkout.session.async_payment_succeeded")
def my_handler(event, **kwargs):
    transaction.on_commit(do_something)
