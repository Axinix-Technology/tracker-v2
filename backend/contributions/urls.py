from django.urls import path
from contributions.views import WorkStatusAIParseView

urlpatterns = [
    path('ai-parse/', WorkStatusAIParseView.as_view(), name='contributions-ai-parse'),
]

