from django import forms

class AnswerForm(forms.Form):
    answer = forms.CharField(label="Перевод", max_length=100)
