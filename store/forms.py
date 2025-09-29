from django import forms

class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField(required=False)
    mobile = forms.CharField(max_length=20, required=True)  # required mobile
    address = forms.CharField(widget=forms.Textarea, required=True)
    payment_method = forms.ChoiceField(choices=(('cod','Cash on Delivery'), ('stripe','Stripe Checkout')))
