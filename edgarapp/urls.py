# edgarapp/urls.py
from django.urls import path
from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from .views import (
    HomePageView, SearchResultsView, SearchFilingView, AboutView, FaqView, contactView, 
    login_view, register_view, logout_view, account_view, HedgeFundView, PlanView
)

urlpatterns = [
    path('about/', AboutView, name='about'),
    path('faq/', FaqView, name='faq'),
    path('contact/', contactView, name='contact'),
    path('hedgeFunds/', HedgeFundView, name='hedgeFunds'),
    path('search/', SearchResultsView, name='companyOverview'),
    path('filing/', SearchFilingView, name='companyFiling'),

    
    path('', HomePageView, name='home'),

    # member login side
    url(r'^memberhome/$', login_required(TemplateView.as_view(template_name='memberhome.html')), name='memberhome'),
    url(r'^accounts/login/$', login_view, name = 'login'),
    url(r'^accounts/register/$', register_view, name = 'register'),
    url(r'^accounts/logout/$', logout_view, name = "logout"),
    url(r'^account/$', account_view, name = "account"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('pricing/', PlanView, name='pricing'),

]