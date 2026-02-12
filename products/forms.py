from django import forms
from .models import Product


BASE_INPUT_CLASSES = (
    "w-full px-4 py-2 border border-gray-300 dark:border-gray-600 "
    "rounded-lg bg-gray-100/80 dark:bg-gray-700/70 "
    "text-gray-900 dark:text-white "
    "placeholder-gray-400 dark:placeholder-gray-300 "
    "focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
)

FILE_INPUT_CLASSES = (
    "w-full px-4 py-2 border border-gray-300 dark:border-gray-600 "
    "rounded-lg bg-gray-100/80 dark:bg-gray-700/70 "
    "text-gray-900 dark:text-white "
    "file:mr-4 file:py-2 file:px-4 "
    "file:rounded-lg file:border-0 "
    "file:text-sm file:font-semibold "
    "file:bg-blue-500 file:text-white "
    "hover:file:bg-blue-600 "
    "focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
)


class ProductForm(forms.ModelForm):
    # Hauptbild
    main_image = forms.ImageField(
        required=False,
        label="Hauptbild",
        help_text="Hauptproduktbild (empfohlen)",
        widget=forms.FileInput(attrs={
            "class": FILE_INPUT_CLASSES,
            "accept": "image/*",
        })
    )
    
    # Zusätzliche Bilder (max. 5)
    additional_image_1 = forms.ImageField(
        required=False,
        label="Zusätzliches Bild 1",
        widget=forms.FileInput(attrs={
            "class": FILE_INPUT_CLASSES,
            "accept": "image/*",
        })
    )
    additional_image_2 = forms.ImageField(
        required=False,
        label="Zusätzliches Bild 2",
        widget=forms.FileInput(attrs={
            "class": FILE_INPUT_CLASSES,
            "accept": "image/*",
        })
    )
    additional_image_3 = forms.ImageField(
        required=False,
        label="Zusätzliches Bild 3",
        widget=forms.FileInput(attrs={
            "class": FILE_INPUT_CLASSES,
            "accept": "image/*",
        })
    )
    additional_image_4 = forms.ImageField(
        required=False,
        label="Zusätzliches Bild 4",
        widget=forms.FileInput(attrs={
            "class": FILE_INPUT_CLASSES,
            "accept": "image/*",
        })
    )
    additional_image_5 = forms.ImageField(
        required=False,
        label="Zusätzliches Bild 5",
        widget=forms.FileInput(attrs={
            "class": FILE_INPUT_CLASSES,
            "accept": "image/*",
        })
    )
    
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
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Bildvalidierung
        image_fields = [
            'main_image',
            'additional_image_1',
            'additional_image_2',
            'additional_image_3',
            'additional_image_4',
            'additional_image_5',
        ]
        
        for field_name in image_fields:
            image = cleaned_data.get(field_name)
            if image:
                # Maximale Größe: 10MB
                if image.size > 10 * 1024 * 1024:
                    self.add_error(field_name, "Bild ist zu groß. Maximale Größe: 10MB")
                
                # Erlaubte Formate
                allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if hasattr(image, 'content_type') and image.content_type not in allowed_types:
                    self.add_error(field_name, "Ungültiges Bildformat. Erlaubt: JPEG, PNG, GIF, WebP")
        
        return cleaned_data