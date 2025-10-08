class LayDataError(Exception):
    def __init__(self, message: str, status_code: int = 500, code: str | None = None):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class ValidationError(LayDataError):
    def __init__(self, message: str, code: str | None = None):
        super().__init__(message, 400, code)


class AuthError(LayDataError):
    def __init__(self, message: str, code: str | None = None):
        super().__init__(message, 401, code)


class PermissionError(LayDataError):
    def __init__(self, message: str, code: str | None = None):
        super().__init__(message, 403, code)


class ResourceNotFoundError(LayDataError):
    def __init__(self, message: str, code: str | None = None):
        super().__init__(message, 404, code)


class ConflictError(LayDataError):
    def __init__(self, message: str, code: str | None = None):
        super().__init__(message, 409, code)


class ServerError(LayDataError):
    def __init__(self, message: str, code: str | None = None):
        super().__init__(message, 500, code)


class NetworkError(LayDataError):
    def __init__(self, message: str, code: str | None = None):
        super().__init__(message, 503, code)


class TimeoutError(LayDataError):
    def __init__(self, message: str, code: str | None = None):
        # 504 Gateway Timeout semantics
        super().__init__(message, 504, code)


class FieldTypeMismatchError(ValidationError):
    def __init__(self, field_name: str, expected_type: str, actual_type: str, code: str | None = None):
        message = f"Field type mismatch for '{field_name}': expected {expected_type}, got {actual_type}"
        super().__init__(message, code)
        self.field_name = field_name
        self.expected_type = expected_type
        self.actual_type = actual_type


class ErrorContext:
    """Context object to collect error information for beautified error messages."""
    
    def __init__(self):
        self.url: str | None = None
        self.method: str | None = None
        self.status_code: int | None = None
        self.fields: dict | None = None
        self.payload: dict | None = None
        self.record_id: str | None = None
        self.table_id: str | None = None
        self.base_id: str | None = None
        self.file_path: str | None = None
        self.file_url: str | None = None
        self.operation: str | None = None
        self.additional_info: dict = {}
    
    def set_request_info(self, url: str, method: str = None):
        self.url = url
        self.method = method
    
    def set_response_info(self, status_code: int):
        self.status_code = status_code
    
    def set_table_info(self, table_id: str, base_id: str = None):
        self.table_id = table_id
        self.base_id = base_id
    
    def set_record_info(self, record_id: str):
        self.record_id = record_id
    
    def set_payload_info(self, fields: dict = None, payload: dict = None):
        self.fields = fields
        self.payload = payload
    
    def set_attachment_info(self, file_path: str = None, file_url: str = None):
        self.file_path = file_path
        self.file_url = file_url
    
    def set_operation(self, operation: str):
        self.operation = operation
    
    def add_info(self, key: str, value):
        self.additional_info[key] = value
    
    def format_error_message(self, original_message: str) -> str:
        """Format a beautified error message with all collected context."""
        lines = []
        
        # Header with operation and status
        if self.operation:
            lines.append(f"🚨 {self.operation} failed")
        else:
            lines.append("🚨 Request failed")
        
        if self.status_code:
            lines.append(f"   Status: {self.status_code}")
        
        # URL and method
        if self.url:
            method_part = f"{self.method} " if self.method else ""
            lines.append(f"   URL: {method_part}{self.url}")
        
        # Table/Base context
        if self.table_id:
            base_part = f" (base: {self.base_id})" if self.base_id else ""
            lines.append(f"   Table: {self.table_id}{base_part}")
        
        # Record context
        if self.record_id:
            lines.append(f"   Record: {self.record_id}")
        
        # Payload information
        if self.fields:
            lines.append(f"   Fields: {self._format_dict(self.fields)}")
        
        if self.payload and self.payload != self.fields:
            lines.append(f"   Payload: {self._format_dict(self.payload)}")
        
        # Attachment information
        if self.file_path:
            lines.append(f"   File Path: {self.file_path}")
        
        if self.file_url:
            lines.append(f"   File URL: {self.file_url}")
        
        # Additional info
        if self.additional_info:
            for key, value in self.additional_info.items():
                lines.append(f"   {key}: {self._format_value(value)}")
        
        # Original error message
        lines.append(f"   Error: {original_message}")
        
        return "\n".join(lines)
    
    def _format_dict(self, d: dict, max_items: int = 5) -> str:
        """Format a dictionary for display, limiting items."""
        if not d:
            return "{}"
        
        items = list(d.items())[:max_items]
        formatted_items = []
        
        for key, value in items:
            if isinstance(value, str) and len(value) > 50:
                value = value[:47] + "..."
            formatted_items.append(f"{key}: {self._format_value(value)}")
        
        if len(d) > max_items:
            formatted_items.append(f"... and {len(d) - max_items} more")
        
        return "{" + ", ".join(formatted_items) + "}"
    
    def _format_value(self, value) -> str:
        """Format a value for display."""
        if isinstance(value, str):
            if len(value) > 100:
                return f'"{value[:97]}..."'
            return f'"{value}"'
        elif isinstance(value, (list, tuple)):
            if len(value) > 3:
                return f"[{len(value)} items]"
            return str(value)
        elif isinstance(value, dict):
            return f"{{dict with {len(value)} keys}}"
        else:
            return str(value)


def build_error_context(
    *,
    operation: str,
    url: str,
    method: str,
    status_code: int | None = None,
    table_id: str | None = None,
    base_id: str | None = None,
    record_id: str | None = None,
    fields: dict | None = None,
    payload: dict | None = None,
    file_path: str | None = None,
    file_url: str | None = None,
    extra: dict | None = None,
) -> ErrorContext:
    """Helper to construct an ErrorContext with common fields in one call."""
    ctx = ErrorContext()
    ctx.set_operation(operation)
    ctx.set_request_info(url, method)
    if status_code is not None:
        ctx.set_response_info(status_code)
    if table_id is not None or base_id is not None:
        ctx.set_table_info(table_id, base_id)
    if record_id is not None:
        ctx.set_record_info(record_id)
    if fields is not None or payload is not None:
        ctx.set_payload_info(fields, payload)
    if file_path is not None or file_url is not None:
        ctx.set_attachment_info(file_path, file_url)
    if extra:
        for k, v in extra.items():
            ctx.add_info(k, v)
    return ctx


def map_teable_error(status: int, message: str, code: str | None = None, context: ErrorContext = None) -> LayDataError:
    error_map = {
        400: ValidationError,
        401: AuthError,
        403: PermissionError,
        404: ResourceNotFoundError,
        409: ConflictError,
        500: ServerError,
        503: NetworkError,
    }
    error_class = error_map.get(status, ServerError)
    
    # Use beautified message if context is provided
    if context:
        formatted_message = context.format_error_message(message)
        return error_class(formatted_message, code)
    else:
        return error_class(message, code)

