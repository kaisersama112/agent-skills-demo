import re
from typing import Optional, Dict, Any


class SecurityError(Exception):
    """安全错误"""
    pass


class SecurityChecker:
    """安全检查器"""
    
    # 危险的JavaScript函数
    DANGEROUS_JS_FUNCTIONS = {
        "fetch", "XMLHttpRequest", "eval", "Function", "execScript",
        "document.write", "document.writeln", "document.domain",
        "window.open", "window.location", "window.top", "window.parent",
        "localStorage", "sessionStorage", "IndexedDB", "WebSQL"
    }
    
    # 危险的HTML标签
    DANGEROUS_HTML_TAGS = {
        "script", "iframe", "object", "embed", "link", "meta",
        "base", "form", "input", "button"
    }
    
    # 危险的属性
    DANGEROUS_ATTRIBUTES = {
        "onload", "onerror", "onclick", "onmouseover", "onkeydown",
        "onkeyup", "onchange", "onsubmit", "onfocus", "onblur",
        "href", "src", "action", "method"
    }
    
    @classmethod
    def sanitize_html(cls, html: str) -> str:
        """清理HTML代码"""
        # 检查危险标签
        for tag in cls.DANGEROUS_HTML_TAGS:
            if re.search(rf'<\s*{tag}[^>]*>', html, re.IGNORECASE):
                raise SecurityError(f"禁止使用危险HTML标签: {tag}")
        
        # 检查危险属性
        for attr in cls.DANGEROUS_ATTRIBUTES:
            if re.search(rf'{attr}\s*=', html, re.IGNORECASE):
                raise SecurityError(f"禁止使用危险属性: {attr}")
        
        # 检查危险JavaScript函数
        for func in cls.DANGEROUS_JS_FUNCTIONS:
            if re.search(rf'\b{re.escape(func)}\s*\(', html):
                raise SecurityError(f"禁止使用危险JavaScript函数: {func}")
        
        # 检查内联样式中的危险内容
        if re.search(r'style\s*=\s*["\'].*expression\(.*["\']', html, re.IGNORECASE):
            raise SecurityError("禁止使用内联样式中的expression")
        
        return html
    
    @classmethod
    def check_js_safety(cls, js_code: str) -> bool:
        """检查JavaScript代码安全性"""
        # 检查危险函数
        for func in cls.DANGEROUS_JS_FUNCTIONS:
            if re.search(rf'\b{re.escape(func)}\s*\(', js_code):
                return False
        
        # 检查危险操作
        dangerous_patterns = [
            r'\bwindow\.location\s*=',
            r'\bdocument\.cookie\s*=',
            r'\beval\s*\(',
            r'\bFunction\s*\(',
            r'\bexecScript\s*\(',
            r'\bnew\s+Function\s*\(',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, js_code):
                return False
        
        return True
    
    @classmethod
    def validate_sandbox_app(cls, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证沙箱应用数据"""
        if "html_content" in app_data:
            app_data["html_content"] = cls.sanitize_html(app_data["html_content"])
        
        return app_data
