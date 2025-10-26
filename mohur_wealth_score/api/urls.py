from django.urls import path
from .views import WealthScoreView

urlpatterns = [
    # Defines the URL for our score calculation endpoint
    # e.g., POST /api/v1/calculate-score/
    path('calculate-score/', WealthScoreView.as_view(), name='calculate-score'),
]
