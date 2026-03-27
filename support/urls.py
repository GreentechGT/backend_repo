from django.urls import path
from .views import FAQListView, SupportMessageCreateView

urlpatterns = [
    path('faqs/', FAQListView.as_view(), name='faq-list'),
    path('message/', SupportMessageCreateView.as_view(), name='support-message-create'),
]
