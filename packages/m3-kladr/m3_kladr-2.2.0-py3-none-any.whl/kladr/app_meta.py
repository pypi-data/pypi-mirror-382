# coding:utf-8

from django.conf.urls import url
from m3 import authenticated_user_required

from .actions import kladr_controller, KLADRPack, Kladr_DictPack


def register_actions():
    kladr_controller.packs.extend(
        (
            KLADRPack(),
            Kladr_DictPack()
        )
    )


@authenticated_user_required
def kladr_view(request):
    return kladr_controller.process_request(request)


def register_urlpatterns():
    u"""
    Регистрация конфигурации урлов для приложения kladr
    """
    return [
        url(r'^m3-kladr', kladr_view),
    ]
