# Security Documentation

## Overview

This document outlines the security measures, best practices, and protocols for the Personal Drive application to ensure data protection and secure operations.

## Security Architecture

### Authentication & Authorization
- **Appwrite Integration**: Leverages Appwrite's built-in authentication system (via Flutter SDK)
- **User Authentication**: Handled by Flutter Appwrite SDK (JWT tokens managed by SDK)
- **API Key Authentication**: Python service requires `X-API-Key` header for all endpoints
- **User Context**: User ID passed via `X-User-Id` header (set by Flutter after Appwrite auth)
- **Single-User System**: Users can only access their own files and data
- **Session Management**: Secure session handling with proper expiration (Appwrite SDK)
- **ALL API endpoints MUST require authentication** (except `/health` and `/`)
- **Appwrite API Key**: Used server-side only for Tables API operations

### Data Protection

#### Encryption
- **In Transit**: All communications use TLS 1.3
- **At Rest**: Files stored in S3-compatible storage (B2/R2) are encrypted
- **Database**: Sensitive data encrypted using industry-standard algorithms
- **API Keys**: Securely stored as environment variables (.env), never hardcoded
- **NEVER expose S3 credentials, API keys, or secrets to Flutter client**

#### File Security
- **Access Control**: Single-user system with user-scoped data access
- **Pre-signed URLs**: Time-limited upload/download URLs (15 min upload, 1 hour download)
- **File uploads/downloads MUST use presigned URLs** (generated server-side)
- **File Type Validation**: Whitelist of allowed MIME types
- **File Size Limits**: Maximum 100MB per file upload
- **File Name Sanitization**: Prevent path traversal attacks

### API Security

#### Rate Limiting
- **Function Calls**: 1000 requests per hour per user
- **File Uploads**: 100 uploads per hour per user
- **Search Queries**: 5000 requests per hour per user

#### Input Validation (ALL inputs MUST be validated)
- **File Names**: Sanitized to prevent path traversal attacks (alphanumeric + hyphens only)
- **File Sizes**: Maximum 100MB per file upload (validated)
- **MIME Types**: Whitelist of allowed file types (validated)
- **Search Queries**: Length-limited (max 500 chars, validated)
- **File IDs**: Validated (alphanumeric + hyphens only)
- **ALL inputs MUST be validated and sanitized** before processing

### Infrastructure Security

#### Appwrite Functions
- **Execution Isolation**: Each function runs in isolated containers
- **Resource Limits**: CPU and memory constraints prevent abuse
- **Dependency Scanning**: Regular security audits of npm packages

#### Python Service (Unified Backend)
- **Container Security**: Docker images built from minimal base images
- **Network Isolation**: Services communicate through private networks
- **Secret Management**: API keys stored in environment variables (.env)
- **Direct client access**: Accessible directly from Flutter client (with API key authentication)
- **Thread Safety**: Lock for FAISS index updates
- **Input Validation**: All inputs validated and sanitized
- **User Context Validation**: User ID verified for all user operations

## Security Best Practices

### Development
1. **Code Reviews**: All changes require security review
2. **Dependency Updates**: Regular security patch updates
3. **Security Testing**: Automated vulnerability scanning
4. **Secret Rotation**: Regular API key and credential updates
5. **NEVER put secrets in client code**: All secrets server-side only
6. **NEVER skip authentication**: All endpoints require authentication (API key + user context)
7. **NEVER allow direct client → S3**: Presigned URLs only
8. **ALWAYS validate user context**: Verify X-User-Id header matches authenticated user
9. **ALWAYS use API key authentication**: Python service requires X-API-Key header

### Deployment
1. **Environment Separation**: Distinct dev, staging, and production environments
2. **Backup Encryption**: All backups encrypted with strong keys
3. **Monitoring**: Real-time security event monitoring
4. **Incident Response**: Documented procedures for security incidents

## Compliance

### Data Privacy
- **GDPR Compliance**: Right to deletion, data portability, and consent management
- **Data Retention**: Automatic cleanup of temporary files after 30 days
- **User Consent**: Clear privacy policy and terms of service
- **Data Export**: Users can export all their data in standard formats

### Audit Logging
- **Access Logs**: All file access attempts logged with timestamps
- **Authentication Logs**: Login attempts and session management events
- **Function Execution**: Appwrite function calls logged for debugging
- **Search Queries**: Search activity logged for analytics and security
- **Never log sensitive data**: Passwords, tokens, file contents excluded
- **Include request IDs**: For tracing requests across services
- **Structured logging**: Where possible for better analysis

## Threat Model

### Identified Threats
1. **Unauthorized Access**: Mitigated through strong authentication
2. **Data Breach**: Prevented with encryption and access controls
3. **Denial of Service**: Limited through rate limiting and resource constraints
4. **Malicious Uploads**: Blocked through file validation and scanning
5. **Insider Threats**: Reduced through audit logging and access monitoring

### Security Controls
- **Preventive**: Authentication, encryption, input validation
- **Detective**: Logging, monitoring, anomaly detection
- **Corrective**: Incident response, backup restoration, patching

## Incident Response

### Response Team
- **Primary Contact**: Security lead engineer
- **Secondary Contact**: DevOps team lead
- **Escalation**: CTO for critical incidents

### Response Procedures
1. **Detection**: Automated alerts for suspicious activities
2. **Containment**: Immediate isolation of affected systems
3. **Investigation**: Root cause analysis and impact assessment
4. **Remediation**: Fix vulnerabilities and restore services
5. **Communication**: Notify affected users within 72 hours
6. **Documentation**: Post-incident report and lessons learned

## Security Checklist

### Pre-Deployment
- [ ] Security code review completed
- [ ] Vulnerability scan passed
- [ ] Dependencies updated to latest secure versions
- [ ] Environment variables configured with production secrets
- [ ] Backup and recovery procedures tested

### Post-Deployment
- [ ] Security monitoring enabled
- [ ] Log aggregation configured
- [ ] Incident response procedures documented
- [ ] User security notifications sent
- [ ] Compliance audit scheduled

## Contact

For security concerns or to report vulnerabilities, please contact:
- **Security Team**: security@personal-drive.app
- **Emergency**: security-emergency@personal-drive.app

---

Last Updated: 2024-12-19