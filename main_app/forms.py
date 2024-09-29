# main_app/forms.py

from django import forms

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Chọn file Excel',
        help_text='File phải có định dạng .xlsx với 5 sheet và 4 cột: symbol, volume, signal, date.'
    )