"""twiliotutorial URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

import twiliotutorial.views as app_views

urlpatterns = [
    path('callback', app_views.InteractiveVoiceResponseView.as_view(), name='twilio-callback'),
    path('play-again', app_views.PlayAgain.as_view(), name='play-again'),
    path('beerfact', app_views.BeerFact.as_view(), name='beerfact'),
    path('beertext', app_views.BeerText.as_view(), name='beertext'),

]
