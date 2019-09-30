from django.urls import path

from . import views

app_name = 'quotes'
urlpatterns = [
    path('', views.ListView.as_view(), name='list'),
    path('new', views.NewView.as_view(), name='new'),
    path('<int:pk>', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/update', views.UpdateView.as_view(), name='update'),
    path('<int:pk>/delete', views.DeleteView.as_view(), name='delete'),
]
