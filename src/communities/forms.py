from django import forms

class InviteForm(forms.Form):
    expiration = forms.ChoiceField(choices=[
        ('1h', '1 Hour'),
        ('1d', '1 Day'),
        ('1w', '1 Week'),
        ('1m', '1 Month'),
        ('never', 'Never')
    ])
    max_uses = forms.NumberInput()
