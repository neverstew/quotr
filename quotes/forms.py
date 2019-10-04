from django import forms

class QuoteSearchForm(forms.Form):
    search = forms.CharField(
        label="Search",
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search'})
    )