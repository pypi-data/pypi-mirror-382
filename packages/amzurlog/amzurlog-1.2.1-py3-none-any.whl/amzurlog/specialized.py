"""
AmzurLog Specialized Logging
============================

This module provides specialized logging categories for enterprise applications:
- Security event logging
- Audit trail logging
- API request/response logging
- LLM interaction logging
- Error event logging
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json

from .core import AmzurLogger, LogLevel
from .context import log_context


class SecurityLogger:
    """Specialized logger for security events"""
    
    def __init__(self, logger: AmzurLogger):
        self.logger = logger
        
    def security_event(
        self,
        message: str,
        event_type: str,
        ip: str,
        user_agent: str,
        request_id: str = None,
        user_id: str = None,
        path: str = None,
        method: str = None,
        status_code: int = None,
        **kwargs
    ):
        """Log a security event with comprehensive context"""
        security_data = {
            'log_type': 'security',
            'event_type': event_type,
            'ip_address': ip,
            'user_agent': user_agent,
            'request_id': request_id or 'unknown',
            'user_id': user_id or 'anonymous',
            'timestamp': datetime.utcnow().isoformat(),
            'severity': 'high'
        }
        
        if path:
            security_data['path'] = path
        if method:
            security_data['method'] = method
        if status_code:
            security_data['status_code'] = status_code
            
        security_data.update(kwargs)
        
        self.logger.warning(message, **security_data)
        
    def suspicious_activity(
        self,
        message: str,
        activity_type: str,
        risk_level: str = 'medium',
        **kwargs
    ):
        """Log suspicious activity"""
        self.security_event(
            message,
            event_type='suspicious_activity',
            activity_type=activity_type,
            risk_level=risk_level,
            **kwargs
        )
        
    def authentication_event(
        self,
        message: str,
        auth_result: str,
        user_id: str = None,
        **kwargs
    ):
        """Log authentication events"""
        self.security_event(
            message,
            event_type='authentication',
            auth_result=auth_result,
            user_id=user_id,
            **kwargs
        )


class AuditLogger:
    """Specialized logger for audit events and compliance"""
    
    def __init__(self, logger: AmzurLogger):
        self.logger = logger
        
    def audit_event(
        self,
        message: str,
        action: str,
        user_id: str,
        resource: str,
        resource_id: str = None,
        status: str = 'success',
        **kwargs
    ):
        """Log an audit event for compliance tracking"""
        audit_data = {
            'log_type': 'audit',
            'action': action,
            'user_id': user_id or 'anonymous',
            'resource': resource,
            'resource_id': resource_id,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'compliance': True
        }
        
        audit_data.update(kwargs)
        
        self.logger.info(message, **audit_data)
        
    def data_access(
        self,
        message: str,
        user_id: str,
        data_type: str,
        operation: str,
        record_count: int = None,
        **kwargs
    ):
        """Log data access events"""
        self.audit_event(
            message,
            action='data_access',
            user_id=user_id,
            resource=data_type,
            operation=operation,
            record_count=record_count,
            **kwargs
        )
        
    def privilege_change(
        self,
        message: str,
        user_id: str,
        target_user: str,
        old_privileges: list,
        new_privileges: list,
        **kwargs
    ):
        """Log privilege changes"""
        self.audit_event(
            message,
            action='privilege_change',
            user_id=user_id,
            resource='user_privileges',
            resource_id=target_user,
            old_privileges=old_privileges,
            new_privileges=new_privileges,
            **kwargs
        )


class APILogger:
    """Specialized logger for API requests and responses"""
    
    def __init__(self, logger: AmzurLogger):
        self.logger = logger
        
    def api_request(
        self,
        message: str,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        duration: int,
        user_id: str = None,
        request_body: str = None,
        response_body: str = None,
        **kwargs
    ):
        """Log API request with full context"""
        api_data = {
            'log_type': 'api_request',
            'request_id': request_id,
            'method': method.upper(),
            'path': path,
            'status_code': status_code,
            'duration_ms': duration,
            'user_id': user_id or 'anonymous',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if request_body:
            if isinstance(request_body, str):
                api_data['request_body'] = request_body[:1000]  # Limit size
            else:
                api_data['request_body'] = str(request_body)[:1000]
        if response_body:
            if isinstance(response_body, str):
                api_data['response_body'] = response_body[:1000]  # Limit size
            else:
                api_data['response_body'] = str(response_body)[:1000]
            
        api_data.update(kwargs)
        
        # Choose log level based on status code
        if status_code >= 500:
            level = LogLevel.ERROR
        elif status_code >= 400:
            level = LogLevel.WARNING
        else:
            level = LogLevel.INFO
            
        self.logger._log(level, message, **api_data)
        
    def api_error(
        self,
        message: str,
        request_id: str,
        method: str,
        path: str,
        error_type: str,
        error_message: str,
        **kwargs
    ):
        """Log API errors"""
        self.api_request(
            message,
            request_id=request_id,
            method=method,
            path=path,
            status_code=500,
            duration=0,
            error_type=error_type,
            error_message=error_message,
            **kwargs
        )


class LLMLogger:
    """Specialized logger for LLM/AI interactions"""
    
    def __init__(self, logger: AmzurLogger):
        self.logger = logger
        
    def llm_interaction(
        self,
        message: str,
        user_id: str,
        model: str,
        tokens: int,
        duration: int,
        cost: float = None,
        prompt_tokens: int = None,
        completion_tokens: int = None,
        **kwargs
    ):
        """Log LLM interaction with usage metrics"""
        llm_data = {
            'log_type': 'llm_interaction',
            'user_id': user_id or 'anonymous',
            'model': model,
            'total_tokens': tokens,
            'duration_ms': duration,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if cost is not None:
            llm_data['cost_usd'] = cost
        if prompt_tokens is not None:
            llm_data['prompt_tokens'] = prompt_tokens
        if completion_tokens is not None:
            llm_data['completion_tokens'] = completion_tokens
            
        llm_data.update(kwargs)
        
        self.logger.info(message, **llm_data)
        
    def llm_error(
        self,
        message: str,
        user_id: str,
        model: str,
        error_type: str,
        error_message: str,
        **kwargs
    ):
        """Log LLM errors"""
        self.llm_interaction(
            message,
            user_id=user_id,
            model=model,
            tokens=0,
            duration=0,
            error_type=error_type,
            error_message=error_message,
            status='failed',
            **kwargs
        )
        
    def llm_cost_alert(
        self,
        message: str,
        user_id: str,
        daily_cost: float,
        monthly_cost: float,
        threshold: float,
        **kwargs
    ):
        """Log cost alerts for LLM usage"""
        self.logger.warning(
            message,
            log_type='llm_cost_alert',
            user_id=user_id,
            daily_cost=daily_cost,
            monthly_cost=monthly_cost,
            threshold=threshold,
            **kwargs
        )


class ErrorLogger:
    """Specialized logger for error events and exceptions"""
    
    def __init__(self, logger: AmzurLogger):
        self.logger = logger
        
    def error_event(
        self,
        message: str,
        error_type: str,
        error_message: str,
        stack_trace: str = None,
        user_id: str = None,
        request_id: str = None,
        function_name: str = None,
        response_body: Any = None,
        **kwargs
    ):
        """Log detailed error information"""
        error_data = {
            'log_type': 'error_event',
            'error_type': error_type,
            'error_message': error_message,
            'timestamp': datetime.utcnow().isoformat(),
            'severity': 'error'
        }
        
        if stack_trace:
            error_data['stack_trace'] = stack_trace
        if user_id:
            error_data['user_id'] = user_id
        if request_id:
            error_data['request_id'] = request_id
        if function_name:
            error_data['function_name'] = function_name
        if response_body:
            if isinstance(response_body, str):
                error_data['response_body'] = response_body[:1000]  # Limit size
            else:
                error_data['response_body'] = str(response_body)[:1000]
            
        error_data.update(kwargs)
        
        self.logger.error(message, **error_data)
        
    def database_error(
        self,
        message: str,
        operation: str,
        table: str,
        error_message: str,
        query: str = None,
        **kwargs
    ):
        """Log database errors"""
        self.error_event(
            message,
            error_type='DatabaseError',
            error_message=error_message,
            database_operation=operation,
            table=table,
            query=query[:200] if query else None,  # Limit query size
            **kwargs
        )
        
    def validation_error(
        self,
        message: str,
        field: str,
        value: str,
        validation_rule: str,
        **kwargs
    ):
        """Log validation errors"""
        self.error_event(
            message,
            error_type='ValidationError',
            error_message=f"Validation failed for field '{field}'",
            field=field,
            invalid_value=str(value)[:100],  # Limit value size
            validation_rule=validation_rule,
            **kwargs
        )


class SpecializedLoggers:
    """Container for all specialized loggers"""
    
    def __init__(self, base_logger: AmzurLogger):
        self.security = SecurityLogger(base_logger)
        self.audit = AuditLogger(base_logger)
        self.api = APILogger(base_logger)
        self.llm = LLMLogger(base_logger)
        self.error = ErrorLogger(base_logger)
        
    @classmethod
    def create(cls, logger_name: str = "specialized") -> 'SpecializedLoggers':
        """Create specialized loggers with a new base logger"""
        from .core import AmzurLogger
        base_logger = AmzurLogger(logger_name)
        return cls(base_logger)