# -*- encoding: utf-8 -*-
"""
@File Name      :   backends.py    
@Create Time    :   2022/4/7 17:15
@Description    :   
@Version        :   
@License        :   MIT
@Author         :   diklios
@Contact Email  :   diklios5768@gmail.com
@Github         :   https://github.com/diklios5768
@Blog           :   
@Motto          :   All our science, measured against reality, is primitive and childlike - and yet it is the most precious thing we have.
"""
__auth__ = 'diklios'

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.validators import validate_email

from Common.utils.auth.verification import verify_verification_code
from Common.utils.http.exceptions import ValidationError, ParameterError
from Common.utils.text_handler.validator import validate_phone_number

UserModel = get_user_model()


class UserBackend(ModelBackend):
    def authenticate(self, request, username: str = None, password: str = None, **kwargs):
        email = kwargs.get('email', None)
        phone_number = kwargs.get('phone_number', None)
        verification_code = kwargs.get('verification_code', None)
        # user = UserModel._default_manager.get_by_natural_key(username)
        if username or email or phone_number:
            user = None
            if username:

                user = UserModel.objects.get(username=username)
            elif username := kwargs.get(UserModel.USERNAME_FIELD, ''):
                user = UserModel.objects.get(**{UserModel.USERNAME_FIELD: username})
            elif email:
                if not validate_email(email):
                    raise ValidationError('Invalid email address.')
                user = UserModel.objects.get(email=email)
            elif phone_number:
                if not validate_phone_number(phone_number):
                    raise ValidationError('Invalid phone number.')
                user = UserModel.objects.get(phone_number=phone_number)
            # 验证用户是否存在
            if not user:
                raise ValidationError(msg='User dose not exist.', chinese_msg='用户不存在')
            # 验证用户密码或者验证码
            if password:
                if user.check_password(password):
                    # Run the default password hasher once to reduce the timing
                    # difference between an existing and a nonexistent user (#20760).
                    # 使用密码验证
                    return user if self.user_can_authenticate(user) else None
                # 处理数据库管理后台的登录逻辑，因为官方和本项目自定义的判断逻辑不大一样
                elif user.is_superuser:
                    return None
                else:
                    # UserModel().set_password(password)
                    raise ValidationError(msg='Password is incorrect.', chinese_msg='密码错误')
            elif verification_code:
                email_login = verify_verification_code('email', email, verification_code, 'login') if email else False
                email_register_and_login = verify_verification_code(
                    'email', email, verification_code, 'register_and_login') if email else False
                phone_number_login = verify_verification_code('phone_number', phone_number, verification_code, 'login') \
                    if phone_number else False
                phone_number_register_and_login = verify_verification_code(
                    'phone_number', phone_number, verification_code, 'register_and_login') if phone_number else False
                if email_login or email_register_and_login or phone_number_login or phone_number_register_and_login:
                    return user if self.user_can_authenticate(user) else None
                else:
                    raise ValidationError(msg='Verification_code is incorrect.', chinese_msg='验证码错误')
            else:
                raise ParameterError('password or verification_code is required')
            # return super().authenticate(request, username, password, **kwargs)
        else:
            raise ParameterError('username or email or phone_number app_name or platform_name  is required')
