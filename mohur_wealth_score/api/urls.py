from django.urls import path
from .views import WealthScoreView

urlpatterns = [
    
    path('calculate-score/', WealthScoreView.as_view(), name='calculate-score'),
]
