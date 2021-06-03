from django import forms
from django.core.mail import send_mail
class UrlForm(forms.Form):
    url = forms.CharField(label = "ENTER URL", required=True)

    def clean(self):
            url = self.cleaned_data.get("url")
            values = {
                "url" : url
            }

            return values

class UrlForm2(forms.Form):
    url = forms.CharField(label = "Url'yi girin", required=True)
    url2 = forms.CharField(label = "Url'yi girin" , required=True)
    
    def clean(self):
            url = self.cleaned_data.get("url")
            url2 = self.cleaned_data.get("url2")
            values = {
                "url" : url,
                "url2": url2
            }

            return values

class ContactForm(forms.Form):
    url = forms.CharField(max_length=100, label="Benzerliği hesaplanacak Url'yi girin:")
    webkume = forms.CharField(widget=forms.Textarea, label="Benzerliği hesaplanacak kümeyi girin:")
    def clean(self):
            url = self.cleaned_data.get("url")
            webkume = self.cleaned_data.get("webkume")
            values = {
                "url" : url,
                "webkume": webkume
            }

            return values