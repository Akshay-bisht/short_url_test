from short.models import MyUser


class UserManagement(object):

    def get_user_by_email(self, email):
        return MyUser.objects.filter(email=email).first()