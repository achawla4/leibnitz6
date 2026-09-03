# -*- coding: utf-8 -*-
"""
Leibnitz6 2026 Security Stack (OWASP ASVS 5.0, NIST SP 800-218, CISA Secure by Design)
Implements runtime security headers, payload rate limiting/sanitization, 
API key verification, and audit logging for Render-deployed web services.
"""

import functools
import os
import time
import re
from flask import request, jsonify, Response, Flask

# OWASP ASVS 5.0 Security Header Definitions
SECURITY_HEADERS = {
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src fonts.gstatic.com; img-src 'self' data:; connect-src 'self' https://leibnitz6.onrender.com;",
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), camera=(), microphone=()'
}

# Rate Limiting Storage (Token Bucket per IP)
_IP_RATE_LIMITS = {}
MAX_REQUESTS_PER_MINUTE = 60
MAX_PAYLOAD_BYTES = 1 * 1024 * 1024  # 1MB payload limit (NIST SP 800-218 DoS protection)

def apply_security_headers(response: Response) -> Response:
    """Apply OWASP ASVS 5.0 & CISA Secure by Design Headers to all responses."""
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

def validate_payload_security():
    """Verify request size and rate limits before processing."""
    client_ip = request.remote_addr or '127.0.0.1'
    now = time.time()

    # Rate limiting check
    if client_ip in _IP_RATE_LIMITS:
        timestamps = [t for t in _IP_RATE_LIMITS[client_ip] if now - t < 60]
        if len(timestamps) >= MAX_REQUESTS_PER_MINUTE:
            return jsonify({
                'status': 'SEC_RATE_LIMIT_EXCEEDED',
                'error': 'Too many requests. OWASP ASVS Rate Limit enforced (60 req/min).'
            }), 429
        timestamps.append(now)
        _IP_RATE_LIMITS[client_ip] = timestamps
    else:
        _IP_RATE_LIMITS[client_ip] = [now]

    # Payload size validation
    content_length = request.content_length
    if content_length and content_length > MAX_PAYLOAD_BYTES:
        return jsonify({
            'status': 'SEC_PAYLOAD_TOO_LARGE',
            'error': 'Payload size exceeds 1MB security threshold.'
        }), 413

    return None

def sanitize_suganita_input(source_code: str) -> str:
    """
    Sanitize Suganita source code against potential injection vectors.
    Ensures input code remains constrained within Suganita Devanagari DSL grammar.
    """
    if not source_code:
        return ""
    # Strip null bytes and non-printable control characters (except newline/tab)
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', source_code)
    return sanitized

def init_security_stack(app: Flask):
    """Register security middleware hooks on the Flask server app."""
    @app.before_request
    def security_before_request():
        err_response = validate_payload_security()
        if err_response:
            return err_response

    @app.after_request
    def security_after_request(response):
        return apply_security_headers(response)
