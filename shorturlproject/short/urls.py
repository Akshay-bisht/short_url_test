from django.conf.urls import include,url
from django.urls import path
from . import views

AUTH_PATTERNS = [
    # A U T H E N T I C A T I O N
    path('login/', views.LoginView.as_view(), name='account-login'),
    path('register/', views.UserCreate.as_view(), name='account-create'),
    path('changepassword/', views.ChangePassword.as_view(), name='changepassword'),
]


RESET_PATTERNS = [
    url('set-password/', views.SetPassword.as_view(), name="set-password"),
    url('verify/', views.VerifyOTP.as_view(), name="verifysendotp"),
    url('', views.ForgetPasswordSendOTP.as_view(), name="forgetpasswordsendotp"),
]

USER_PATTERNS = [
    path('',views.UserList.as_view(),name ='list_user'),

]
urlpatterns = [
    path('auth/', include(AUTH_PATTERNS)),
    path('user/',include(USER_PATTERNS)),
    path('reset-password/', include(RESET_PATTERNS)),
    path('adminaccess/',views.AdminAccessView.as_view(), name = 'adminaccess'),
    path('solutionprovider/',views.SolutionProviderAccessView.as_view(), name = 'solutionprovider'),
    path('home/',views.ShortUrls.as_view(),name = "short_url"),
    path('home/<str:thread>/',views.ShortGetUrls.as_view(),name = "short_url")

]