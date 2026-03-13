from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email","username", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # remove help text
        for field in self.fields.values():
            field.help_text = None

        # add CSS classes
        self.fields['email'].widget.attrs.update({'class': 'input-box'})
        self.fields['username'].widget.attrs.update({'class': 'input-box'})
        self.fields['password1'].widget.attrs.update({'class': 'input-box'})
        self.fields['password2'].widget.attrs.update({'class': 'input-box'})