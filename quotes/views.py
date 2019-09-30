from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from .models import Quote

# Create your views here.
class IndexView(generic.base.TemplateView):
    template_name = 'quotr/index.html'

class ListView(LoginRequiredMixin, generic.ListView):
    model = Quote
    paginate_by = 20
    
class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Quote

class NewView(LoginRequiredMixin, generic.CreateView):
    model = Quote
    fields = ['book', 'text', 'page']
    success_url = reverse_lazy('quotes:list')

class UpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Quote
    fields = ['book', 'text', 'page']

class DeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Quote
    success_url = reverse_lazy('quotes:list')

