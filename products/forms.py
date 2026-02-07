from django import forms
from .models import Product


BASE_INPUT_CLASSES = (
    "w-full px-4 py-2 border border-gray-300 dark:border-gray-600 "
    "rounded-lg bg-gray-100/80 dark:bg-gray-700/70 "
    "text-gray-900 dark:text-white "
    "placeholder-gray-400 dark:placeholder-gray-300 "
    "focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "title",
            "description",
            "price",
            "meta_title",
            "meta_description",
            "meta_keywords",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASSES,
                "placeholder": "Product title",
            }),
            "description": forms.Textarea(attrs={
                "class": BASE_INPUT_CLASSES,
                "rows": 5,
                "placeholder": "Product description",
            }),
            "price": forms.NumberInput(attrs={
                "class": BASE_INPUT_CLASSES,
                "step": "0.01",
                "placeholder": "0.00",
            }),
            "meta_title": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASSES,
                "placeholder": "SEO meta title",
            }),
            "meta_description": forms.Textarea(attrs={
                "class": BASE_INPUT_CLASSES,
                "rows": 3,
                "placeholder": "SEO meta description",
            }),
            "meta_keywords": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASSES,
                "placeholder": "keyword1, keyword2, keyword3",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": (
                    "w-5 h-5 text-blue-600 rounded "
                    "border-gray-300 dark:border-gray-600 "
                    "bg-gray-100 dark:bg-gray-700 "
                    "focus:ring-blue-500"
                ),
            }),
        }
