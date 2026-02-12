# products/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import Product, ProductImage
from .forms import ProductForm
from .utils import upload_to_imgbb


@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            
            # Hauptbild hochladen
            main_image = request.FILES.get('main_image')
            if main_image:
                upload_result = upload_to_imgbb(main_image)
                if upload_result:
                    product.main_image_url = upload_result['url']
                    product.main_image_thumb_url = upload_result['thumb_url']
                    product.main_image_medium_url = upload_result['medium_url']
                    product.main_image_delete_url = upload_result['delete_url']
                else:
                    messages.error(request, "Hauptbild konnte nicht hochgeladen werden.")
                    return render(request, "products/product_form.html", {
                        "form": form,
                        "title": "Create Product",
                    })
            
            product.save()
            
            # Zusätzliche Bilder hochladen
            additional_images = []
            for i in range(1, 6):
                image = request.FILES.get(f'additional_image_{i}')
                if image:
                    upload_result = upload_to_imgbb(image)
                    if upload_result:
                        additional_images.append({
                            'order': i - 1,
                            'url': upload_result['url'],
                            'thumb_url': upload_result['thumb_url'],
                            'medium_url': upload_result['medium_url'],
                            'delete_url': upload_result['delete_url'],
                        })
                    else:
                        messages.warning(request, f"Zusätzliches Bild {i} konnte nicht hochgeladen werden.")
            
            # ProductImage Objekte erstellen
            for img_data in additional_images:
                ProductImage.objects.create(
                    product=product,
                    image_url=img_data['url'],
                    thumb_url=img_data['thumb_url'],
                    medium_url=img_data['medium_url'],
                    delete_url=img_data['delete_url'],
                    order=img_data['order']
                )
            
            messages.success(request, "Produkt erfolgreich erstellt!")
            return redirect("company_dashboard")
    else:
        form = ProductForm()

    return render(request, "products/product_form.html", {
        "form": form,
        "title": "Create Product",
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # View Counter
    Product.objects.filter(id=product.id).update(views=models.F("views") + 1)
    
    # Zusätzliche Bilder laden
    additional_images = product.additional_images.all()

    return render(request, "products/product_detail.html", {
        "product": product,
        "additional_images": additional_images,
    })


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            
            # Hauptbild aktualisieren wenn hochgeladen
            main_image = request.FILES.get('main_image')
            if main_image:
                upload_result = upload_to_imgbb(main_image)
                if upload_result:
                    product.main_image_url = upload_result['url']
                    product.main_image_thumb_url = upload_result['thumb_url']
                    product.main_image_medium_url = upload_result['medium_url']
                    product.main_image_delete_url = upload_result['delete_url']
                    messages.success(request, "Hauptbild erfolgreich aktualisiert!")
                else:
                    messages.error(request, "Hauptbild konnte nicht hochgeladen werden.")
            
            product.save()
            
            # Zusätzliche Bilder hochladen (nur neue)
            current_count = product.additional_images.count()
            for i in range(1, 6):
                image = request.FILES.get(f'additional_image_{i}')
                if image and current_count < 5:
                    upload_result = upload_to_imgbb(image)
                    if upload_result:
                        ProductImage.objects.create(
                            product=product,
                            image_url=upload_result['url'],
                            thumb_url=upload_result['thumb_url'],
                            medium_url=upload_result['medium_url'],
                            delete_url=upload_result['delete_url'],
                            order=current_count
                        )
                        current_count += 1
                        messages.success(request, f"Zusätzliches Bild {i} hochgeladen!")
                    else:
                        messages.warning(request, f"Zusätzliches Bild {i} konnte nicht hochgeladen werden.")
                elif image and current_count >= 5:
                    messages.warning(request, "Maximale Anzahl (5) zusätzlicher Bilder erreicht.")
                    break
            
            messages.success(request, "Produkt erfolgreich aktualisiert!")
            return redirect("company_dashboard")
    else:
        form = ProductForm(instance=product)

    return render(request, "products/product_form.html", {
        "form": form,
        "title": "Edit Product",
        "product": product,
    })


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Produkt erfolgreich gelöscht!")
        return redirect("company_dashboard")

    return render(request, "products/product_confirm_delete.html", {
        "product": product
    })


@login_required
def product_image_delete(request, pk):
    """Löscht ein zusätzliches Produktbild"""
    image = get_object_or_404(ProductImage, pk=pk, product__owner=request.user)
    product_pk = image.product.pk
    
    if request.method == "POST":
        image.delete()
        messages.success(request, "Bild erfolgreich gelöscht!")
        return redirect("product_edit", pk=product_pk)
    
    return render(request, "products/product_image_confirm_delete.html", {
        "image": image
    })

from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render

def product_list(request):
    # Base queryset - immer geboostete zuerst
    products = Product.objects.filter(is_active=True)
    
    # Suchparameter auslesen
    search_query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    sort = request.GET.get("sort", "").strip()
    
    # 🔍 TEXT-SUCHE
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(meta_keywords__icontains=search_query) |
            Q(meta_description__icontains=search_query)
        )
    
    # 🏷️ KATEGORIE-FILTER
    if category_id and category_id.isdigit():
        products = products.filter(category_id=int(category_id))
    
    # 💰 PREIS-FILTER
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # 📊 SORTIERUNG - IMMER erst nach is_boosted, dann nach Auswahl
    if sort == "price_asc":
        products = products.order_by("-is_boosted", "price", "-created_at")
    elif sort == "price_desc":
        products = products.order_by("-is_boosted", "-price", "-created_at")
    elif sort == "newest":
        products = products.order_by("-is_boosted", "-created_at")
    elif sort == "name":
        products = products.order_by("-is_boosted", "title", "-created_at")
    else:
        # STANDARD: Geboostete zuerst, dann nach Relevanz/Datum
        products = products.order_by("-is_boosted", "-created_at")
    
    # 📄 PAGINATION
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    # Kategorien für Dropdown
    categories = []  # Ersetze mit: Category.objects.all().order_by("name")
    
    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "categories": categories,
        "selected_category": category_id,
        "q": search_query,
        "min_price": min_price,
        "max_price": max_price,
        "sort": sort,
    }
    
    return render(request, "products/product_list.html", context)