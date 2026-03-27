from rest_framework import generics, permissions
from .models import SupportMessage, FAQ
from .serializers import SupportMessageSerializer, FAQSerializer

class FAQListView(generics.ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [permissions.AllowAny]

class SupportMessageCreateView(generics.CreateAPIView):
    queryset = SupportMessage.objects.all()
    serializer_class = SupportMessageSerializer
    permission_classes = [permissions.AllowAny] # Allow anyone to submit support messages

    def perform_create(self, serializer):
        # Automatically attach user if authenticated
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()
