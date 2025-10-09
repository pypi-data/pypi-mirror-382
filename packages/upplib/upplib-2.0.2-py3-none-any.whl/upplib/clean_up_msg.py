from upplib import *
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Union


def clean_up_msg_1(msg: str = None) -> str:
    try:
        """
            2025-09-28T19:38:41.146-06:00 com.leo.digest.aop.ApiLogAspect - traceId: - (catTraceId:rcs-gateway-0a0f2154-488625-102) - ===>API GatewayFacadeImpl#gatewayRequest START
            ->
            2025-09-28T20:09:52.390-06:00 o.rcs.biz.limiter.XLimitSwitc - rcs-gateway-0a0f2154-488625-102 - xlimit No current limiter configured，key=mobilewalla_mbmultiagents

            2025-09-29T10:26:55.161-06:00 c.c.f.a.spring.annotation.SpringValueProcessor - traceId: - Monitoring key: spring.mvc.servlet.path, beanName: swaggerWelcome, field: org.springdoc.webmvc.ui.SwaggerWelcomeWebMvc.mvcServletPath
            ->
            2025-09-29T10:26:55.161-06:00 annotation.SpringValueProcessor - - Monitoring key: spring.mvc.servlet.path, beanName: swaggerWelcome, field: org.springdoc.webmvc.ui.SwaggerWelcomeWebMvc.mvcServletPath
        """
        TIME_DEMO = '2025-09-28T20:09:52.390-06:00'
        CAT_TRACE_ID_DEMO = '(catTraceId:rcs-gateway-0a0f2154-488625-102)'
        SEP_S = '- traceId: -'
        time = msg[0:len(TIME_DEMO)]
        msg1 = msg[len(TIME_DEMO):].split(SEP_S)
        method = msg1[0][-31:-2]
        if len(method) < 29:
            method = ' ' * (29 - len(method)) + method
        if msg1[1].strip().startswith('(catTraceId:'):
            trace_id = msg1[1][0:len(CAT_TRACE_ID_DEMO) + 1]
            other = msg1[1][len(trace_id) + 2:].strip()
            trace_id = re.search(r'\(catTraceId:([^)]+)\)', trace_id).group(1)
        else:
            trace_id = ''
            other = msg1[1].strip()
        return f'{time} {method} {trace_id} - {other}'
    except Exception as e:
        return msg
