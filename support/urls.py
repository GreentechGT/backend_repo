from django.urls import path
from .views import faq_list, support_message_create

urlpatterns = [
    path('faqs/', faq_list, name='faq-list'),
    path('message/', support_message_create, name='support-message-create'),
]
