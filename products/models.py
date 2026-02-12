# products/models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Product(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products"
    )

    # Core
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_boosted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Main Image (ImgBB URLs)
    main_image_url = models.URLField(max_length=500, blank=True, null=True)
    main_image_thumb_url = models.URLField(max_length=500, blank=True, null=True)
    main_image_medium_url = models.URLField(max_length=500, blank=True, null=True)
    main_image_delete_url = models.URLField(max_length=500, blank=True, null=True)

    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    # Tracking
    views = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_boosted", "-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["owner"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if not self.meta_title:
            self.meta_title = self.title

        if not self.meta_description:
            self.meta_description = self.description[:160]

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    """Zusätzliche Produktbilder (max. 5)"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="additional_images"
    )
    
    # ImgBB URLs
    image_url = models.URLField(max_length=500)
    thumb_url = models.URLField(max_length=500, blank=True, null=True)
    medium_url = models.URLField(max_length=500, blank=True, null=True)
    delete_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Reihenfolge
    order = models.PositiveSmallIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]
        
    def __str__(self):
        return f"Image {self.order + 1} for {self.product.title}"