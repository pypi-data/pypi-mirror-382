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
            
            2025-10-09T11:29:30.561+08:00 [http-nio-8080-exec-5097] INFO  com.leo.rcs.biz.aspect.RcsReportAspect - traceId: - (catTraceId:datafeaturecore-0a5a030c-488883-287895) - RequestBody:{"bizData":{"user_id":1073850014231710218,"gaid":"364de12f-2fc9-4769-b2b6-e0b47bdf841d"},"extContext":{"mainDecisionId":"20251009112924085WITHDRAW02124","standardScene":"WITHDRAW"},"ignoreCache":false,"ignoreStatus":false,"interfaceId":"mobilewalla","methodId":"multiagents"}
            ->
            2025-10-09T11:29:30.561+08:00 [http-nio-8080-exec-5097] INFO  com.leo.rcs.biz.aspect.RcsReportAspect - datafeaturecore-0a5a030c-488883-287895 - RequestBody:{"bizData":{"user_id":1073850014231710218,"gaid":"364de12f-2fc9-4769-b2b6-e0b47bdf841d"},"extContext":{"mainDecisionId":"20251009112924085WITHDRAW02124","standardScene":"WITHDRAW"},"ignoreCache":false,"ignoreStatus":false,"interfaceId":"mobilewalla","methodId":"multiagents"}
        """
        TIME_DEMO = '2025-09-28T20:09:52.390-06:00'
        # CAT_TRACE_ID_DEMO = '(catTraceId:rcs-gateway-0a0f2154-488625-102)'
        SEP_S = '- traceId: -'
        time = msg[0:len(TIME_DEMO)]
        msg1 = msg[len(TIME_DEMO):].split(SEP_S)
        method = msg1[0][-31:-2]
        other = msg1[1]
        if len(method) < 29:
            method = ' ' * (29 - len(method)) + method
        if other.strip().startswith('(catTraceId:'):
            trace_id = re.search(r'\(catTraceId:([^)]+)\)', msg1[1]).group(1)
            other = other[other.find(trace_id) + len(trace_id):].strip()
        else:
            trace_id = ''
            other = other.strip()
        if other.strip().startswith(' - '):
            other = other[3:].strip()
        return f'{time} {method} {trace_id} - {other}'
    except Exception as e:
        return msg
