from django.contrib.auth.hashers import check_password  # 添加这行
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):  # 确保使用check_password
                return user
        except User.DoesNotExist:
            return None