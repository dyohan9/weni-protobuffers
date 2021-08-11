import stripe
from weni.billing import Gateway, GatewayNotConfigured
from django.conf import settings


class StripeGateway(Gateway):
    default_currency = "BRL"
    display_name = "Stripe"

    def __init__(self):
        billing_settings = getattr(settings, "BILLING_SETTINGS")
        if not billing_settings or not billing_settings.get("stripe"):
            raise GatewayNotConfigured(
                "The '%s' gateway is not correctly " "configured." % self.display_name
            )
        stripe_settings = billing_settings["stripe"]
        stripe.api_key = stripe_settings["API_KEY"]
        self.stripe = stripe

    def authorize(self, identification, options: dict = None):
        try:
            resp = self.stripe.SetupIntent.create(customer=identification)
            return {"status": "SUCCESS", "response": resp}
        except self.stripe.error.InvalidRequestError as error:
            return {"status": "FAILURE", "response": error}

    def purchase(self, money: float, identification, options: dict = None):
        try:
            payment = stripe.PaymentMethod.list(
                customer=identification,
                type="card",
            )
            response = stripe.PaymentIntent.create(
                amount=int(money * 100),
                currency=self.default_currency.lower(),
                customer=identification,
                payment_method=payment.get("data", {})[0].get("id"),
                off_session=True,
                confirm=True,
                metadata=options,
            )
        except self.stripe.error.CardError as error:
            return {"status": "FAILURE", "response": error}
        return {"status": "SUCCESS", "response": response}