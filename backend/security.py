"""
Security middleware for KrishiSetu API
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import hashlib
from collections import defaultdict
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    def __init__(self):
        self.request_history: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: Dict[str, float] = {}
        self.suspicious_patterns = [
            "script", "javascript", "vbscript", "onload", "onerror",
            "../", "..\\", "etc/passwd", "cmd.exe", "powershell"
        ]
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is temporarily blocked"""
        if ip in self.blocked_ips:
            if time.time() - self.blocked_ips[ip] < 300:  # 5 minute block
                return True
            else:
                del self.blocked_ips[ip]
        return False
    
    def block_ip(self, ip: str):
        """Temporarily block an IP address"""
        self.blocked_ips[ip] = time.time()
        logger.warning(f"Blocked IP {ip} for suspicious activity")
    
    def check_request_pattern(self, request: Request) -> bool:
        """Check for suspicious request patterns"""
        # Check URL for suspicious patterns
        url_str = str(request.url).lower()
        for pattern in self.suspicious_patterns:
            if pattern in url_str:
                return False
        
        # Check headers for suspicious content
        for header_name, header_value in request.headers.items():
            if any(pattern in header_value.lower() for pattern in self.suspicious_patterns):
                return False
        
        return True
    
    def validate_content_type(self, request: Request) -> bool:
        """Validate content type for file uploads"""
        if request.method == "POST" and "/predict" in str(request.url):
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("multipart/form-data"):
                return False
        return True
    
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        
        # Check if IP is blocked
        if self.is_ip_blocked(client_ip):
            logger.warning(f"Blocked request from {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "IP temporarily blocked due to suspicious activity"}
            )
        
        # Check for suspicious patterns
        if not self.check_request_pattern(request):
            logger.warning(f"Suspicious request pattern from {client_ip}: {request.url}")
            self.block_ip(client_ip)
            return JSONResponse(
                status_code=400,
                content={"detail": "Request blocked due to suspicious content"}
            )
        
        # Validate content type
        if not self.validate_content_type(request):
            logger.warning(f"Invalid content type from {client_ip}")
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid content type"}
            )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Log request details
            process_time = time.time() - start_time
            logger.info(f"{client_ip} - {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
            
            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
            return response
            
        except Exception as e:
            logger.error(f"Request processing error from {client_ip}: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )

def create_security_middleware():
    """Factory function to create security middleware"""
    return SecurityMiddleware()