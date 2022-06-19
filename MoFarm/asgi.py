'''
Author: your name
Date: 2022-03-15 09:54:33
LastEditTime: 2022-03-15 09:54:33
LastEditors: your name
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /SoFuse/MoFarm/asgi.py
'''
"""
ASGI config for SoFuse project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MoFarm.settings')

application = get_asgi_application()
