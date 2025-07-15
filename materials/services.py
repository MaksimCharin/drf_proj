import stripe
from django.conf import settings
from users.models import StripeProductPrice
from materials.models import Course, Lesson

stripe.api_key = settings.STRIPE_SECRET_KEY

def get_or_create_stripe_product_price(item, amount):

    is_course = isinstance(item, Course)
    is_lesson = isinstance(item, Lesson)

    if is_course:
        stripe_details, created = StripeProductPrice.objects.get_or_create(course=item)
    elif is_lesson:
        stripe_details, created = StripeProductPrice.objects.get_or_create(lesson=item)
    else:
        return None

    if created or not stripe_details.stripe_product_id:
        product_name = f"{'Course' if is_course else 'Lesson'}: {item.name}"
        product_description = item.description
        try:
            product = stripe.Product.create(
                name=product_name,
                description=product_description,
            )
            stripe_details.stripe_product_id = product.id
            stripe_details.save()
        except stripe.error.StripeError as e:
            print(f"Ошибка при создании продукта Stripe: {e}")
            return None

    if created or not stripe_details.stripe_price_id:
        try:
            price = stripe.Price.create(
                product=stripe_details.stripe_product_id,
                unit_amount=int(amount * 100),
                currency='usd',
            )
            stripe_details.stripe_price_id = price.id
            stripe_details.save()
        except stripe.error.StripeError as e:
            print(f"Ошибка при создании цены Stripe: {e}")
            return None

    return stripe_details

def create_stripe_checkout_session(price_id, user_email, success_url, cancel_url):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            customer_email=user_email,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return checkout_session.url
    except stripe.error.StripeError as e:
        print(f"Ошибка при создании сессии Stripe: {e}")
        return None
