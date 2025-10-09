from upplib import *
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Union


def clean_up_msg(msg: str = None, clean_up_type: int = 1) -> str:
    if msg is None:
        return ''
    formatters: list[Callable[[str], Optional[str]]] = [
        clean_up_msg_1,
        clean_up_msg_2,
        clean_up_msg_3,
    ]
    formatter_map: dict[int, Callable[[str], Optional[str]]] = {
        i + 1: formatter for i, formatter in enumerate(formatters)
    }
    if clean_up_type in formatter_map:
        return formatter_map[clean_up_type](msg)
    return msg


def clean_up_msg_1(msg: str = None) -> str:
    try:
        """
            2025-09-28T19:38:41.146-06:00 com.leo.digest.aop.ApiLogAspect - traceId: - (catTraceId:rcs-gateway-0a0f2154-488625-102) - ===>API GatewayFacadeImpl#gatewayRequest START
            ->
            2025-09-28T20:09:52.390-06:00 o.rcs.biz.limiter.XLimitSwitc - rcs-gateway-0a0f2154-488625-102 - xlimit No current limiter configured，key=mobilewalla_mbmultiagents


            2025-09-29T10:26:55.161-06:00 c.c.f.a.spring.annotation.SpringValueProcessor - traceId: - Monitoring key: spring.mvc.servlet.path, beanName: swaggerWelcome, field: org.springdoc.webmvc.ui.SwaggerWelcomeWebMvc.mvcServletPath
            ->
            2025-09-29T10:26:55.161-06:00 annotation.SpringValueProcessor - - Monitoring key: spring.mvc.servlet.path, beanName: swaggerWelcome, field: org.springdoc.webmvc.ui.SwaggerWelcomeWebMvc.mvcServletPath
            
            
            2025-10-09T11:29:30.561+08:00 [http-nio-8080-exec-5097] INFO  com.leo.rcs.biz.aspect.RcsReportAspect - traceId: - (catTraceId:datafeaturecore-0a5a030c-488883-287895) - RequestBody:{"bizData":{"user_id":1073850014231710218,"gaid":"364de12f-2fc9-4769-b2b6-e0b47bdf841d"},"extContext":{"mainDecisionId":"20251009112924085WITHDRAW02124","standardScene":"WITHDRAW"},"ignoreCache":false,"ignoreStatus":false,"interfaceId":"mobilewalla","methodId":"multiagents"}
            ->
            2025-10-09T11:29:30.561+08:00 -97- INFO  com.leo.rcs.biz.aspect.RcsReportAspect - datafeaturecore-0a5a030c-488883-287895 - RequestBody:{"bizData":{"user_id":1073850014231710218,"gaid":"364de12f-2fc9-4769-b2b6-e0b47bdf841d"},"extContext":{"mainDecisionId":"20251009112924085WITHDRAW02124","standardScene":"WITHDRAW"},"ignoreCache":false,"ignoreStatus":false,"interfaceId":"mobilewalla","methodId":"multiagents"}
        """
        TIME_DEMO = '2025-09-28T20:09:52.390-06:00'
        # CAT_TRACE_ID_DEMO = '(catTraceId:rcs-gateway-0a0f2154-488625-102)'
        SEP_S = '- traceId: -'
        time = msg[0:len(TIME_DEMO)]
        msg1 = msg[len(TIME_DEMO):].split(SEP_S)
        thread_id = ' '
        msg10 = msg1[0].strip()
        pattern = r'http-nio-(\d+)-exec-(\d+)'
        match = re.search(pattern, msg10)
        if match:
            thread_id = f' -{match.group(2)[-2:]}- '
        method = msg10[-31:]
        other = msg1[1].strip()
        if len(method) < 29:
            method = ' ' * (29 - len(method)) + method
        if other.strip().startswith('(catTraceId:'):
            trace_id = re.search(r'\(catTraceId:([^)]+)\)', msg1[1]).group(1)
            other = other[other.find(trace_id) + len(trace_id) + 1:].strip()
        else:
            trace_id = ''
            other = other.strip()
        if other.strip().startswith('- '):
            other = other[2:].strip()
        return f'{time}{thread_id}{method} - {trace_id} - {other}'
    except Exception as e:
        return msg


def clean_up_msg_2(msg: str = None) -> str:
    try:
        """
            2025-10-09T13:45:49.687+08:00 INFO 8 --- [nio-8080-exec-4] c.l.r.b.s.device.impl.DeviceServiceImpl  : (catTraceId:customer-product-0a5a0329-488885-107496) - checkDeviceId lock key: 1073852969169211259
            ->
            2025-10-09T13:45:49.687+08:00 -04- c.l.r.b.s.device.impl.DeviceServiceImpl - customer-product-0a5a0329-488885-107496 - checkDeviceId lock key: 1073852969169211259
        """
        TIME_DEMO = '2025-09-28T20:09:52.390-06:00'
        SEP_S = ': (catTraceId:'
        time = msg[0:len(TIME_DEMO)]
        msg1 = msg[len(TIME_DEMO):].split(SEP_S)
        method = msg1[0].strip()[-31:]
        other = msg1[1].strip()
        if len(method) < 29:
            method = ' ' * (29 - len(method)) + method
        trace_id = other[0:other.find(') - ')].strip()
        other = other[other.find(trace_id) + len(trace_id) + 3:].strip()
        return f'{time} {method} - {trace_id} - {other}'
    except Exception as e:
        return msg


def clean_up_msg_3(msg: str = None) -> str:
    try:
        """
            2025-10-09T14:25:28.096+07:00 INFO com.itn.idn.review.aop.LogAspect - traceId:db57046b7cba9d5c55fa5ff93727c4df - ReviewBackController.queryCreditCasesByUserIdsV2: request log info-------------> {"userIds":[1011450014961537063]}
            ->
            2025-10-09T14:25:28.096+07:00 com.itn.idn.review.aop.LogAspect - db57046b7cba9d5c55fa5ff93727c4df - ReviewBackController.queryCreditCasesByUserIdsV2: request log info-------------> {"userIds":[1011450014961537063]}
        """
        TIME_DEMO = '2025-09-28T20:09:52.390-06:00'
        SEP_S = ' - traceId:'
        time = msg[0:len(TIME_DEMO)]
        msg1 = msg[len(TIME_DEMO):].split(SEP_S)
        method = msg1[0].strip()[-31:]
        other = msg1[1].strip()
        if len(method) < 29:
            method = ' ' * (29 - len(method)) + method
        trace_id = other[0:other.find(' - ')].strip()
        other = other[other.find(trace_id) + len(trace_id) + 2:].strip()
        return f'{time} {method} - {trace_id} - {other}'
    except Exception as e:
        return msg


def clean_up_msg_4(msg: str = None) -> str:
    try:
        """
            2025-10-09T15:00:33.751+07:00 INFO [TID: N/A] [8] [http-nio-10009-exec-1] [GatewayController] [WITHDRAW-1080478239721884577] Call response: length=632929
            ->
            2025-10-09T15:00:33.751+07:00 -01- GatewayController - WITHDRAW-1080478239721884577 - Call response: length=632929
        """
        TIME_DEMO = '2025-09-28T20:09:52.390-06:00'
        SEP_S = ' - traceId:'
        time = msg[0:len(TIME_DEMO)]
        msg1 = msg[len(TIME_DEMO):].split(SEP_S)
        method = msg1[0].strip()[-31:]
        other = msg1[1].strip()
        if len(method) < 29:
            method = ' ' * (29 - len(method)) + method
        trace_id = other[0:other.find(' - ')].strip()
        other = other[other.find(trace_id) + len(trace_id) + 2:].strip()
        return f'{time} {method} - {trace_id} - {other}'
    except Exception as e:
        return msg
