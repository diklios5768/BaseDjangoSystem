# -*- encoding: utf-8 -*-
"""
@File Name      :   user.py    
@Create Time    :   2022/5/5 15:25
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

from .base.regions import CountryBaseSerializer, ProvinceBaseSerializer, CityBaseSerializer, AreaBaseSerializer, \
    StreetBaseSerializer
from .base.user import user_exclude, UserBaseSerializer


class UserSerializer(UserBaseSerializer):
    # 地址
    country = CountryBaseSerializer()
    province = ProvinceBaseSerializer()
    city = CityBaseSerializer()
    area = AreaBaseSerializer()
    street = StreetBaseSerializer()

    class Meta(UserBaseSerializer.Meta):
        depth = 1
        exclude = user_exclude
