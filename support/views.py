from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import SupportMessage, FAQ
from .serializers import SupportMessageSerializer, FAQSerializer

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def faq_list(request):
    queryset = FAQ.objects.all()
    serializer = FAQSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.AllowAny]) # Allow anyone to submit support messages
def support_message_create(request):
    serializer = SupportMessageSerializer(data=request.data)
    if serializer.is_valid():
        if request.user.is_authenticated:
            serializer.save(user=request.user)
        else:
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
