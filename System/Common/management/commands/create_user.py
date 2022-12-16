# -*- encoding: utf-8 -*-
"""
@File Name      :   create_user.py    
@Create Time    :   2022/4/28 8:59
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

from abc import ABCMeta
from secrets import compare_digest

from django.core.management.base import BaseCommand

from Common.models.user import User


class Command(BaseCommand, metaclass=ABCMeta):
    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', type=str, required=True, help='init username')
        parser.add_argument('-p1', '--password', type=str, help='password')
        parser.add_argument('-p2', '--confirm_password', type=str, help='confirm password')
        parser.add_argument('-e', '--email', type=str, help='email')
        parser.add_argument('-p', '--phone', type=str, help='phone')

    def handle(self, *args, **options):
        username = options.get('username')
        password = options.get('password', None)
        confirm_password = options.get('confirm_password', None)
        if password:
            if not confirm_password:
                print('please input password again')
                return
            if compare_digest(password, confirm_password):
                print('password not equal')
                return
        email = options.get('email', None)
        phone = options.get('phone', None)
        user = User.objects.create_user(username=username, password=password, email=email, phone=phone)
        print('create user success')
