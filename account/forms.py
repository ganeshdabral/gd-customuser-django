from django import forms
from .models import CustomUser

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput)
    password = forms.CharField(widget=forms.PasswordInput)

class UserForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    class Meta:
        model = CustomUser
        fields = '__all__'
        exclude = ["is_admin", "is_verified", "last_login", "password", "activation_key", "key_expires"]

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': '{}'.format(field).replace("_", ' ').capitalize(),

            })
        self.fields['email'].widget.attrs['placeholder'] = 'abc@xyz.com'
        self.fields['email'].required = True
        self.fields['password'].required = True
        self.fields['password2'].required = True
        if self.instance.pk:
            self.fields['username'].required = False
            #self.fields['username'].widget.attrs['readonly'] = True
            self.fields['email'].required = False
            self.fields['email'].widget.attrs['readonly'] = True
            self.fields['password'].widget.attrs['readonly'] = True
            self.fields['password'].required = False
            self.fields['password2'].widget.attrs['readonly'] = True
            self.fields['password2'].required = False
    def clean(self):
        data = self.cleaned_data
        password = self.cleaned_data["password"]
        password2 = self.cleaned_data["password2"]
        if password == password2:
            return data
        raise forms.ValidationError("Password must match")
    '''
    def clean_email(self):
        email = self.cleaned_data["email"]
        user_obj = CustomUser.objects.get(email=email)
        if user_obj.count():
            raise forms.ValidationError("email already exist")
        return email
    
    def clean_username(self):
        username = self.cleaned_data["username"]
        user_obj = CustomUser.objects.get(username=username)
        if user_obj.count():
            raise forms.ValidationError("username already exist")
        return username
    '''
class UserUpdateForm(forms.ModelForm):
    is_update = forms.CharField(widget=forms.HiddenInput, initial="user")
    class Meta:
        model = CustomUser
        fields = '__all__'
        exclude = ["username", "email", "is_admin", "is_verified", "last_login", "password", "activation_key", "key_expires"]

    def clean_email(self):
        # Check that email is not duplicate
        email = self.cleaned_data["email"]
        try:
            match = CustomUser.objects.exclude(pk=self.instance.pk).get(email=email)
        except CustomUser.DoesNotExist:
            # Unable to find a user, this is fine
            return email
            # A user was found with this as a username, raise an error.
        raise forms.ValidationError('This email address is already in use.')

class UserChangePasswordForm(forms.ModelForm):
    old_password = forms.CharField(label='current Password', widget=forms.PasswordInput)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    is_update = forms.CharField(widget=forms.HiddenInput, initial="password")
    class Meta:
        model = CustomUser
        fields = ('old_password','password','password2')


    def clean(self):
        data = self.cleaned_data
        password = self.cleaned_data["password"]
        password2 = self.cleaned_data["password2"]
        if password == password2:
            return data
        raise forms.ValidationError("Password must match")