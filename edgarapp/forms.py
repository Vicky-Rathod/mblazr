# edgarapp/forms.py
# for the Contact Form

from django import forms

##########################
###### Contact Form ######

class ContactForm(forms.Form):
  name = forms.CharField(required=True, label='Name')
  email = forms.EmailField(required=True, label='Email')
  message = forms.CharField(required=True, widget=forms.Textarea(attrs={'rows':3, 'cols':40}), label='Mssg')

  def __init__(self, *args, **kwargs):
    super(ContactForm, self).__init__(*args, **kwargs)
    self.fields['name'].widget.attrs.update({
      'placeholder': 'name',
      "name":"name"})
    self.fields['email'].widget.attrs.update({
      'placeholder': 'email address',
      "name":"email"})
    self.fields['message'].widget.attrs.update({
      'placeholder': 'Leave your comment or feedback',
      "name":"message"})



##########################
## User Authentication ##

from django.contrib.auth import authenticate, get_user_model


## Sign in
class UsersLoginForm(forms.Form):
  username = forms.CharField(label=False)
  password = forms.CharField(widget = forms.PasswordInput, label=False)

  def __init__(self, *args, **kwargs):
    super(UsersLoginForm, self).__init__(*args, **kwargs)
    self.fields['username'].widget.attrs.update({
      'class': 'fadeIn second',
      'placeholder': 'username',
      "name":"username"})
    self.fields['password'].widget.attrs.update({
      'class': 'fadeIn second',
      'placeholder': 'password',
      "name":"password"})

  def clean(self, *args, **keyargs):
    username = self.cleaned_data.get("username")
    password = self.cleaned_data.get("password")

    if username and password:
      user = authenticate(username = username, password = password)
      if not user:
        raise forms.ValidationError("This user does not exists")
      if not user.check_password(password):
        raise forms.ValidationError("Incorrect Password")
      if not user.is_active:
        raise forms.ValidationError("User is no longer active")

    return super(UsersLoginForm, self).clean(*args, **keyargs)


## Sign up
User = get_user_model()

class UsersRegisterForm(forms.ModelForm):
  class Meta:
    model = User
    fields = [
      "username",
      "email",
      "password",
    ]
  username = forms.CharField(label=False)
  email = forms.EmailField(label=False)
  password = forms.CharField(widget = forms.PasswordInput, label=False)


  def __init__(self, *args, **kwargs):
    super(UsersRegisterForm, self).__init__(*args, **kwargs)
    self.fields['username'].widget.attrs.update({
        'class': 'fadeIn second',
        'placeholder': 'username',
        "name":"username"})
    self.fields['email'].widget.attrs.update({
        'class': 'fadeIn second',
        'placeholder': 'your email',
        "name":"email"})
    self.fields['password'].widget.attrs.update({
        'class': 'fadeIn second',
        'placeholder': 'password',
        "name":"password"})


  def clean(self, *args, **keyargs):
    email = self.cleaned_data.get("email")
    username = self.cleaned_data.get("username")
    password = self.cleaned_data.get("password")
    
    email_qs = User.objects.filter(email=email)
    if email_qs.exists():
      raise forms.ValidationError("Email is already registered")

    username_qs = User.objects.filter(username=username)
    if username_qs.exists():
      raise forms.ValidationError("User with this username already registered")
    
    # can add more validations for password
    if len(password) < 8: 
      raise forms.ValidationError("Password must be greater than 8 characters")


    return super(UsersRegisterForm, self).clean(*args, **keyargs)

