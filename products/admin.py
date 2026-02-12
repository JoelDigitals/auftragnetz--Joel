# products/admin.py
from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 5
    fields = ['image_url', 'thumb_url', 'order']
    readonly_fields = ['image_url', 'thumb_url']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'owner', 
        'price', 
        'is_active', 
        'is_boosted',
        'views',
        'has_main_image',
        'created_at'
    ]
    list_filter = ['is_active', 'is_boosted', 'created_at', 'owner']
    search_fields = ['title', 'description', 'meta_keywords']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = [
        'slug', 
        'views', 
        'created_at', 
        'updated_at',
        'main_image_url',
        'main_image_thumb_url',
        'main_image_delete_url'
    ]
    
    fieldsets = (
        ('Grundinformationen', {
            'fields': ('owner', 'title', 'slug', 'description', 'price')
        }),
        ('Hauptbild', {
            'fields': ('main_image_url', 'main_image_thumb_url', 'main_image_delete_url'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_boosted')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Statistiken', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline]
    
    def has_main_image(self, obj):
        return bool(obj.main_image_url)
    has_main_image.boolean = True
    has_main_image.short_description = 'Hauptbild'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'created_at', 'image_preview']
    list_filter = ['created_at', 'product']
    search_fields = ['product__title']
    readonly_fields = ['image_url', 'thumb_url', 'delete_url', 'image_preview']
    
    fieldsets = (
        ('Produkt', {
            'fields': ('product', 'order')
        }),
        ('Bild URLs', {
            'fields': ('image_url', 'thumb_url', 'delete_url', 'image_preview')
        }),
    )
    
    def image_preview(self, obj):
        if obj.thumb_url:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 200px;" />',
                obj.thumb_url
            )
        return '-'
    image_preview.short_description = 'Vorschau'


from django.utils.html import format_html