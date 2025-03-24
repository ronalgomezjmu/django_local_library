from django.urls import path
from . import views
from .api import api

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),  # Ensure this line is present
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path("api/", api.urls),
]


# # Use include() to add paths from the catalog application
# from django.urls import include

# urlpatterns += [
#     path('catalog/', include('catalog.urls')),
# ]
