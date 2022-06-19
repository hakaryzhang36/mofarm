'''
Author: your name
Date: 2022-03-15 09:55:11
LastEditTime: 2022-03-15 09:55:11
LastEditors: your name
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /SoFuse/MoFarm/wsgi.py
'''
"""
WSGI config for MoFarm project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MoFarm.settings')

application = get_wsgi_application()
