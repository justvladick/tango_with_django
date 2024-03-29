from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from booktime import forms
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from booktime import models
import logging
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import HttpResponseRedirect
# from django.contrib.auth import logout
# from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import (
    FormView, CreateView, UpdateView, DeleteView, )
from django.urls import reverse
from django import forms as django_forms
from django.db import models as django_models
import django_filters
from django_filters.views import FilterView

from booktime.models import Order


def home(request):
    variable = 555
    return render(request, 'home.html', {'variable': variable})


class ContactUsView(FormView):
    template_name = "contact_form.html"
    form_class = forms.ContactForm
    success_url = "/booktime"

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)


class ProductListView(ListView):
    template_name = "booktime/product_list.html"
    paginate_by = 4

    def get_queryset(self):
        tag = self.kwargs['tag']
        self.tag = None
        if tag != "all":
            self.tag = get_object_or_404(
                models.ProductTag, slug=tag
            )
        if self.tag:
            products = models.Product.objects.active().filter(
                tags=self.tag
            )
        else:
            products = models.Product.objects.active()
        return products.order_by("name")

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['tag'] = self.kwargs['tag']
        return context


logger = logging.getLogger(__name__)


# class SignupView(FormView):
#     template_name = "signup.html"
#     form_class = forms.UserCreationForm
#
#     def get_success_url(self):
#         redirect_to = self.request.GET.get("next", "/")
#         return redirect_to
#
#     def form_valid(self, form):
#         response = super().form_valid(form)
#         form.save()
#         email = form.cleaned_data.get("email")
#         raw_password = form.cleaned_data.get("password1")
#         logger.info(
#             "New signup for email=%s through SignupView", email
#         )
#         user = authenticate(email=email, password=raw_password)
#         login(self.request, user)
#         form.send_mail()
#         messages.info(
#             self.request, "You signed up successfully."
#         )
#         return response


class AddressListView(LoginRequiredMixin, ListView):
    model = models.Address

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = models.Address
    fields = [
        "name", "address1", "address2",
        "zip_code", "city", "country",
    ]
    success_url = reverse_lazy("booktime:address_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Address
    fields = [
        "name", "address1", "address2",
        "zip_code", "city", "country",
    ]
    success_url = reverse_lazy("booktime:address_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Address
    success_url = reverse_lazy("booktime:address_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


def add_to_basket(request):
    product = get_object_or_404(
        models.Product, pk=request.GET.get("product_id")
    )
    basket = request.basket
    if not request.basket:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
        basket = models.Basket.objects.create(user=user)
        request.session["basket_id"] = basket.id

    basketline, created = models.BasketLine.objects.get_or_create(
        basket=basket, product=product
    )
    if not created:
        basketline.quantity += 1
        basketline.save()
    return HttpResponseRedirect(
        reverse("booktime:product", args=(product.slug,))
    )


def manage_basket(request):
    if not request.basket:
        return render(request, "basket.html", {"formset": None})
    if request.method == "POST":
        formset = forms.BasketLineFormSet(
            request.POST, instance=request.basket
        )
        if formset.is_valid():
            formset.save()
    else:
        formset = forms.BasketLineFormSet(
            instance=request.basket
        )
    if request.basket.is_empty():
        return render(request, "basket.html", {"formset": None})

    return render(request, "basket.html", {"formset": formset})


class AddressSelectionView(LoginRequiredMixin, FormView):
    template_name = "address_select.html"
    form_class = forms.AddressSelectionForm
    success_url = reverse_lazy('booktime:checkout_done')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        del self.request.session['basket_id']
        basket = self.request.basket
        basket.create_order(
            form.cleaned_data['billing_address'],
            form.cleaned_data['shipping_address']
        )
        return super().form_valid(form)


class DateInput(django_forms.DateInput):
    input_type = 'date'


class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = models.Order
        fields = {
            'user__email': ['icontains'],
            'status': ['exact'],
            'date_updated': ['gt', 'lt'],
            'date_added': ['gt', 'lt'],
        }
        filter_overrides = {
            django_models.DateTimeField: {
                'filter_class': django_filters.DateFilter,
                'extra': lambda f: {
                    'widget': DateInput}}}


class OrderView(UserPassesTestMixin, FilterView):
    filterset_class = OrderFilter
    login_url = reverse_lazy("auth_login")

    def test_func(self):
        return self.request.user.is_staff is True


# def room(request, order_id):
#     return render(
#         request,
#         "chat_room.html",
#         {"room_name_json": str(order_id)},
#     )


@login_required
def rooms(request):
    orders = Order.objects.filter(user=request.user)
    return render(
        request,
        "customer_service.html",
        {"orders": orders},
    )
