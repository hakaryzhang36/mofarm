'''
Author: lgm
Date: 2022-03-22 14:23:19
LastEditTime: 2022-03-22 14:23:19
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /MoFarm/MoFarmBackEnd/check.py
'''
from functools import wraps
import json
from django.http import HttpResponse
 
 
def request_verify(request_method: str, need_params=None):
    """
        在views方法上加装饰器 例如：@request_verify('get', ['id'])
        :param request_method:
        :param need_params:
        :return:
    """
 
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            method = str(request.method).lower()
            # 先判断类型，类型不符合，直接return
            if request_method and not method == request_method.lower():
                response = "method {0} not allowed for: {1}".format(request.method, request.path)
                return response_failure(response)
 
            request.params = {}
            # 暂时不用get请求传参，get的情况可以先忽略
            if method == 'get':
                if not request.GET:
                    if need_params:
                        response = "缺少参数"
                        return response_failure(response)
                else:
                    params = {}
                    request_params = request.GET
                    for item in request_params:
                        params.update({item: request_params.get(item)})
                    # get 必填参数校验
                    if need_params:
                        for need_param_name in need_params:
                            if not params.get(need_param_name):
                                response = "参数 {0} 不能为空".format(need_param_name)
                                return response_failure(response)
                    request.params = params
            else:  # method == post
                if not request.body or request.body == {}:  # 参数为空的情况下
                    if need_params:  # 验证必传
                        response = "缺失参数"
                        return response_failure(response)
                else:  # 非空的时候，尝试去获取参数
                    try:
                        real_request_params = json.loads(request.body)  # 这边要try一下，如果前端传参不是json，json.loads会异常
                    except Exception as e:
                        response = "参数格式不合法"
                        return response_failure(response)
                    # 取出来以后再去判断下必填项是否每一项都有值
                    if need_params:
                        for need_param_name in need_params:
                            if not real_request_params.get(need_param_name):
                                # 如果必传参数取出来是'' (PS: 没传和传了''通过get取出来都是'')，就抛出
                                response = "参数 {0} 不能为空".format(need_param_name)
                                return response_failure(response)
                    # 一直到这里都无异常那么就可以把参数塞进request对象了，避免view里还要再去json.loads
                    request.params = real_request_params
            return func(request, *args, **kwargs)
 
        return inner
 
    return decorator
 
 
def request_post_verify(request_method: str, need_params=None):
    """
        在views方法上加装饰器 例如：@request_verify('post', ['id'])
        :param request_method:
        :param need_params:
        :return:
    """
 
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            method = str(request.method).lower()
            # 先判断类型，类型不符合，直接return
            if request_method and not method == request_method.lower():
                response = "method {0} not allowed for: {1}".format(request.method, request.path)
                return response_failure(response)
 
            request.params = {}
            # 暂时不用get请求传参，get的情况可以先忽略
            if method == 'post':
                if not request.POST:
                    if need_params:
                        response = "缺少参数"
                        return response_failure(response)
                else:
                    params = {}
                    request_params = request.GET
                    for item in request_params:
                        params.update({item: request_params.get(item)})
                    # get 必填参数校验
                    if need_params:
                        for need_param_name in need_params:
                            if not params.get(need_param_name):
                                response = "参数 {0} 不能为空".format(need_param_name)
                                return response_failure(response)
                    request.params = params
            else:  # method == post
                if not request.body or request.body == {}:  # 参数为空的情况下
                    if need_params:  # 验证必传
                        response = "缺失参数"
                        return response_failure(response)
                else:  # 非空的时候，尝试去获取参数
                    try:
                        real_request_params = json.loads(request.body)  # 这边要try一下，如果前端传参不是json，json.loads会异常
                    except Exception as e:
                        response = "参数格式不合法"
                        return response_failure(response)
                    # 取出来以后再去判断下必填项是否每一项都有值
                    if need_params:
                        for need_param_name in need_params:
                            if not real_request_params.get(need_param_name):
                                # 如果必传参数取出来是'' (PS: 没传和传了''通过get取出来都是'')，就抛出
                                response = "参数 {0} 不能为空".format(need_param_name)
                                return response_failure(response)
                    # 一直到这里都无异常那么就可以把参数塞进request对象了，避免view里还要再去json.loads
                    request.params = real_request_params
            return func(request, *args, **kwargs)
 
        return inner
 
    return decorator


# 校验结果封装
def response_failure(message):
    return HttpResponse(json.dumps({
        'code': 4000,
        'message': message
    }, ensure_ascii=False), 'application/json')


