import re
from short.models import MyUser, Otp, UrlDetail
from rest_framework.views import APIView
from .serializer import UserSerializer, ChangePasswordSerializer,UrlDetailSerializer
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from trench.views import simplejwt as sjwt
from django.db.models import Q
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .permissions import SolutionProviderPermission
from rest_framework.decorators import authentication_classes, permission_classes
import string
from random import choice
from django.utils import timezone
from short.services import UserManagement
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect

# Create your views here.

class UserCreate(APIView):
    """
    Register api which is able to create new user
    """
    serializer_class = UserSerializer
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, format='json'):
        with transaction.atomic():
            dict = request.data.copy()
            dict['username'] = request.data.get('username', '').lower()
            dict['email'] = request.data.get('email', '').lower()
            serializer = self.serializer_class(data=dict)
            # here we validating the serializer data 
            if serializer.is_valid():
                user = serializer.save()
                p = request.data.get('password')
                if p:
                    user.set_password(p)
                    user.is_active = True
                    user.save()
                    if user:
                        return Response({"message": "USER_CREATED_SUCCESS"}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"password": ["This field is required"]}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"Failed to create New user"},status=status.HTTP_400_BAD_REQUEST)


class LoginView(sjwt.JSONWebTokenLoginOrRequestMFACode):
    """
    An endpoint for login user.
    """

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        if username:
            try:
                request.data.update({'username': username.lower()})
            except:
                try:
                    request.data._mutable = True
                    request.data.update({'username': username.lower()})
                    request.data._mutable = False
                except:
                    pass
        user = MyUser.objects.filter((Q(username=username)|Q(email=username))).first()
        if user == None:
            return Response({"message": "User Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        if user and user.check_password(request.data.get('password')):
            user.is_active = True
            user.save()
        return super().post(request, *args, **kwargs)

class ChangePassword(APIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = MyUser
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
            }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        users = MyUser.objects.all()
        if users:
            return Response(UserSerializer(users, many= True).data, status= status.HTTP_200_OK)
        return Response({"message":"No User present"}, status=status.HTTP_400_BAD_REQUEST)

    """
    with this method you can update the user detail.
    """
    def put(self, request):
        serializer = UserSerializer(instance=request.user, data= request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status= status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminAccessView(APIView):
    """
    Check the permission task that request user is admin or not if it is admin he is able to see the response only
    """
    permission_classes = (IsAdminUser,)

    def get(self, request):
        return Response({"message":"You are a super user thats why you are able to see that content"})


class SolutionProviderAccessView(APIView):
    """
    Check the custom permission as per task so if you are solution provider or admin then you can only able to see those message
    """
    permission_classes = (SolutionProviderPermission,IsAuthenticated)

    def get(self, request):
        return Response({"message":"either you are admin or solution provider thats why you are able to see that content"})


# by default we set permission to IsAuthenticated but if want to remove that permission from a specific class so we used those decorator
@authentication_classes([])
@permission_classes([])
class ForgetPasswordSendOTP(APIView):
    """
    If you forget password it will send you an otp to the mail id you provide
    """

    def post(self, request, format='json'):
        email = request.data.get("email")
        otp = Otp.objects.filter(user__email=email).first()
        if otp:
            otp.delete()
        user = UserManagement().get_user_by_email(email)
        chars = string.digits
        code = ''.join(choice(chars) for _ in range(4))
        otp = Otp.objects.create(user=user, code=code)
        otp.save()
        subject = "Forgot password mail"
        message = f"OTP is {code}"
        # sending the mail
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email,])
        return Response({"message": "USER_OTP_SEND"}, status=status.HTTP_200_OK)


@authentication_classes([])
@permission_classes([])
class VerifyOTP(APIView):
    """
    Verify the OTP that was send to the mail id and update your status to otp verified so you can set new password
    """
    def post(self, request, format='json'):
        now = timezone.now()
        otp = Otp.objects.filter(
            user__email=request.data.get("email"), code=request.data.get('code')).first()
        user = UserManagement().get_user_by_email(request.data.get("email"))
        if otp:
            user.otp_verified = True
            user.save()
            return Response({"message": "OTP_VERIFIED"}, status=status.HTTP_200_OK)
        return Response({"message": "OTP not found resend main again"}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([])
@permission_classes([])
class SetPassword(APIView):
    """
    After otp verfication you can you can set new password
    """
    def post(self, request, format='json'):
        if request.data.get("password")==request.data.get("confirm-password"):
            user = UserManagement().get_user_by_email(request.data.get("email"))
            if user and user.otp_verified:
                user.set_password(request.data.get("password"))
                user.otp_verified = False
                user.save()
                return Response({"message": "Password Updated Successfully"}, status=status.HTTP_200_OK)
            return Response({"message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"Password and confirm password did not matched"},status=status.HTTP_400_BAD_REQUEST)

import random
import string

def random_string(length):
    pool = string.ascii_letters + string.digits
    thread = ''.join(random.choice(pool) for i in range(length))
    if UrlDetail.objects.filter(thread = thread):
        random_string(6)
    return thread

@authentication_classes([])
@permission_classes([])
class ShortUrls(APIView):


    def post(self, request):
        abc = random_string(6)
        print(abc)
        request_data = request.data.copy()
        if 'http' not in request_data['website']:
            request_data['website']= "http://"+request_data['website']
        request_data["thread"]=abc
        serializer = UrlDetailSerializer(data=request_data)
        if serializer.is_valid():
            serializer.save()
            return Response(f"http://127.0.0.1:8000/home/{abc}/", status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@authentication_classes([])
@permission_classes([])
class ShortGetUrls(APIView):

    def get(self, request,thread):
        url = UrlDetail.objects.filter(thread=thread).first()
        if url:
            return HttpResponseRedirect(redirect_to=url.website)
        return Response({"message":"url not found"}, status=status.HTTP_400_BAD_REQUEST)