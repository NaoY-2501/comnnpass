from django import forms

class QueryForm(forms.Form):
    dateFrom = forms.CharField()
    dateTo = forms.CharField()
    keyword = forms.CharField()
    searchType = forms.CharField()
    search = forms.CharField()
