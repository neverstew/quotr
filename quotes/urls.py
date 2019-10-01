from django.urls import path

from . import views

app_name = 'quotes'
urlpatterns = [
    path('quotes/', views.ListQuoteView.as_view(), name='list-quote'),
    path('quotes/new', views.NewQuoteView.as_view(), name='new-quote'),
    path('quotes/<int:pk>', views.DetailQuoteView.as_view(), name='detail-quote'),
    path('quotes/<int:pk>/update', views.UpdateQuoteView.as_view(), name='update-quote'),
    path('quotes/<int:pk>/delete', views.DeleteQuoteView.as_view(), name='delete-quote'),
    path('books/', views.ListBookView.as_view(), name='list-book'),
    path('books/new', views.NewBookView.as_view(), name='new-book'),
    path('books/<int:pk>', views.DetailBookView.as_view(), name='detail-book'),
    path('books/<int:pk>/update', views.UpdateBookView.as_view(), name='update-book'),
    path('books/<int:pk>/delete', views.DeleteBookView.as_view(), name='delete-book'),
]
