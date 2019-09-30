from django.urls import reverse_lazy
from django.views import generic

from .models import Quote

# Create your views here.
class IndexView(generic.base.TemplateView):
    template_name = 'quotes/index.html'

class ListView(generic.ListView):
    model = Quote
    paginate_by = 20

class DetailView(generic.DetailView):
    model = Quote

class NewView(generic.CreateView):
    model = Quote
    fields = ['book', 'text', 'page']
    success_url = reverse_lazy('quotes:list')

class UpdateView(generic.UpdateView):
    model = Quote
    fields = ['book', 'text', 'page']

class DeleteView(generic.DeleteView):
    model = Quote
    success_url = reverse_lazy('quotes:list')

