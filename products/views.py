# products/views.py
from django.shortcuts import render, get_object_or_404
from .models import Product
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProductForm

@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
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

    return render(request, "products/product_detail.html", {
        "product": product
    })

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("company_dashboard")
    else:
        form = ProductForm(instance=product)

    return render(request, "products/product_form.html", {
        "form": form,
        "title": "Edit Product",
    })

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)

    if request.method == "POST":
        product.delete()
        return redirect("company_dashboard")

    return render(request, "products/product_confirm_delete.html", {
        "product": product
    })
