# TalkBridge Authentication Utilities

A comprehensive collection of authentication utilities for user management, security monitoring, and system maintenance in TalkBridge.

## 📁 Overview

This package provides essential tools for managing authentication, user accounts, and security monitoring in the TalkBridge application. All utilities follow security best practices and use Argon2id encryption.

## 🛠️ Available Utilities

### 1. Password Configuration (`password_config.py`)
Centralized password configuration and validation system.

**Features:**
- Unified password standards across all utilities
- Security requirement validation (12+ chars, complexity)
- Production user password management
- Password generation for new users
- Comprehensive validation with detailed feedback

**Usage:**
```python
from talkbridge.auth.utils import PasswordConfig

# Get all production passwords
passwords = PasswordConfig.get_password_summary()

# Validate a password
is_valid, issues = PasswordConfig.validate_password("MyPassword123!")

# Generate secure password for user
password = PasswordConfig.generate_secure_password("newuser")
```

**CLI Usage:**
```bash
python -m talkbridge.auth.utils.password_config
```

### 2. Password Manager (`password_manager.py`)
Secure password creation and management utility.

**Features:**
- Uses centralized PasswordConfig for consistency
- Bulk password updates for existing users
- Password strength validation
- Secure password reset functionality

**Usage:**
```python
from talkbridge.auth.utils import create_secure_passwords

# Run password manager with unified passwords
create_secure_passwords()
```

**CLI Usage:**
```bash
python -m talkbridge.auth.utils.password_manager
```

### 3. User Generator (`user_generator.py`)
Production user creation with security best practices.

**Features:**
- Creates production-ready user accounts
- Uses centralized PasswordConfig for consistent passwords
- Role-based permission assignment
- Argon2id encryption with pepper
- Principle of least privilege

**Usage:**
```python
from talkbridge.auth.utils import generate_secure_users

# Generate production users with unified passwords
generate_secure_users()
```

**CLI Usage:**
```bash
python -m talkbridge.auth.utils.user_generator
```

### 4. User Unlocker (`user_unlocker.py`)
User account unlock and recovery utility.

**Features:**
- Diagnose authentication issues
- Unlock locked user accounts
- Reset passwords to standard patterns
- Create missing production users
- Comprehensive account recovery
- Automated fix for all production users

**Usage:**
```python
from talkbridge.auth.utils import UserUnlocker, unlock_specific_user, unlock_users

# Unlock specific user
success = unlock_specific_user("admin")

# Use full unlocker functionality
unlocker = UserUnlocker()
diagnosis = unlocker.diagnose_user_issues("username")
unlocker.fix_user_account("username")

# Fix all production users
unlock_users()
```

**CLI Usage:**
```bash
python -m talkbridge.auth.utils.user_unlocker
```

### 5. Security Monitor (`security_monitor.py`)
Authentication log analysis and threat detection.

**Features:**
- Real-time log analysis
- Brute force attack detection
- Suspicious username monitoring
- Failed authentication tracking
- Security recommendations
- Automated threat reporting

**Usage:**
```python
from talkbridge.auth.utils import SecurityMonitor, run_security_analysis

# Create monitor instance
monitor = SecurityMonitor()
analysis = monitor.analyze_logs(hours_back=24)

# Or run complete analysis
run_security_analysis()
```

**CLI Usage:**
```bash
python -m talkbridge.auth.utils.security_monitor
```

### 6. Encryption Verifier (`encryption_verifier.py`)
Verify Argon2id encryption migration status.

**Features:**
- Database schema validation
- Encryption method verification
- User encryption status checking
- Migration completeness validation
- Old database file detection

**Usage:**
```python
from talkbridge.auth.utils import verify_encryption_migration

# Verify encryption migration
success, old_files = verify_encryption_migration()
```

**CLI Usage:**
```bash
python -m talkbridge.auth.utils.encryption_verifier
```

## 🔐 Security Features

All utilities implement enterprise-grade security:

- **Argon2id Encryption**: Industry-standard password hashing
- **Pepper Configuration**: Additional security layer beyond salt
- **Rate Limiting**: Protection against brute force attacks
- **Account Lockout**: Automatic protection against repeated failures
- **Audit Logging**: Comprehensive security event tracking
- **Permission Management**: Role-based access control

## 📊 Security Compliance

### Password Requirements
- ✅ Minimum 12 characters
- ✅ Uppercase letters (A-Z)
- ✅ Lowercase letters (a-z)
- ✅ Digits (0-9)
- ✅ Special characters (!@#$%^&*)

### Authentication Security
- ✅ Argon2id with configurable parameters
- ✅ Cryptographic salt generation
- ✅ Pepper for additional security
- ✅ Rate limiting (5 attempts per 5 minutes)
- ✅ Account lockout protection
- ✅ Secure session management

## 🚀 Quick Start

### Installation
```bash
# Install from project root
pip install -e .

# Or add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/talkbridge/src"
```

### Basic Usage
```python
import sys
sys.path.insert(0, 'src')

from talkbridge.auth.utils import (
    create_secure_passwords,
    generate_secure_users,
    SecurityMonitor,
    run_security_analysis,
    verify_encryption_migration
)

# Create production users
generate_secure_users()

# Update passwords
create_secure_passwords()

# Monitor security
monitor = SecurityMonitor()
analysis = monitor.analyze_logs()
print(f"Analyzed {analysis['total_events']} security events")

# Verify encryption
success, issues = verify_encryption_migration()
if success:
    print("✅ Encryption migration verified")
```

## 📁 File Structure

```
src/talkbridge/auth/utils/
├── __init__.py              # Package exports and imports
├── password_manager.py      # Secure password creation and management
├── user_generator.py        # Production user creation
├── security_monitor.py      # Authentication log analysis
├── encryption_verifier.py   # Encryption migration verification
└── README.md               # This documentation
```

## 🔧 Configuration

### Environment Variables
```bash
# Database configuration
export TALKBRIDGE_DB_PATH="data/users.db"

# Security configuration
export TALKBRIDGE_PEPPER="your-secret-pepper-key"

# Development mode (creates dev users)
export TALKBRIDGE_DEV_MODE="false"

# Project root override
export TALKBRIDGE_PROJECT_ROOT="/path/to/talkbridge"

# Data directory override
export TALKBRIDGE_DATA_DIR="/path/to/data"
```

### Database Requirements
- SQLite 3.7+ with foreign key support
- File permissions: 600 (read/write owner only)
- Location: `data/users.db` (configurable)

## 📈 Security Monitoring

### Log Analysis
The security monitor analyzes authentication logs for:

- **Failed Login Attempts**: Track authentication failures
- **Brute Force Detection**: Rapid succession attempts
- **Suspicious Usernames**: Common attack targets (admin, root, etc.)
- **Rate Limiting Events**: Blocked attempts due to rate limits
- **Account Lockouts**: Automatic security responses

### Alert Thresholds
- **Brute Force**: 3+ attempts within 60 seconds
- **High Failure Rate**: 10+ failures per user
- **Suspicious Activity**: Attempts on system usernames
- **Rate Limiting**: Triggered rate limit responses

## 🛡️ Best Practices

### User Management
1. **Always use secure passwords** (12+ characters, complexity)
2. **Assign minimal permissions** (principle of least privilege)
3. **Regular password rotation** (recommended quarterly)
4. **Monitor user activity** (daily security analysis)
5. **Remove unused accounts** (periodic cleanup)

### Security Monitoring
1. **Daily log analysis** (`run_security_analysis()`)
2. **Monitor failed attempts** (investigate patterns)
3. **Review suspicious usernames** (block if necessary)
4. **Check rate limiting** (ensure protection is active)
5. **Audit user permissions** (monthly review)

### Database Security
1. **Secure file permissions** (600 for database file)
2. **Regular backups** (encrypted and offsite)
3. **Monitor database size** (implement log rotation)
4. **Verify encryption** (run migration verifier)
5. **Test recovery procedures** (quarterly drills)

## 🐛 Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure src is in Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/talkbridge/src"

# Or use relative imports from project root
cd /path/to/talkbridge
python -c "import sys; sys.path.insert(0, 'src'); from talkbridge.auth.utils import SecurityMonitor"
```

**Database Connection Issues:**
```bash
# Check database exists and permissions
ls -la data/users.db
# Should show: -rw------- (600 permissions)

# Verify database path in environment
echo $TALKBRIDGE_DB_PATH

# Test database connection
python -c "
import sys; sys.path.insert(0, 'src')
from talkbridge.auth.auth_manager import AuthManager
auth = AuthManager()
print('✅ Database connection successful')
"
```

**Permission Errors:**
```bash
# Fix database permissions
chmod 600 data/users.db

# Ensure data directory exists
mkdir -p data/logs

# Check data directory permissions
ls -la data/
```

### Debug Mode
Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from talkbridge.auth.utils import SecurityMonitor
monitor = SecurityMonitor()
# Debug output will show detailed analysis steps
```

## 📚 API Reference

### SecurityMonitor Class

```python
class SecurityMonitor:
    """Monitor authentication logs for security threats."""

    def __init__(self, log_file: str = "data/logs/errors.log"):
        """Initialize security monitor with log file path."""

    def analyze_logs(self, hours_back: int = 24) -> Dict[str, any]:
        """Analyze recent authentication logs."""
        # Returns analysis with:
        # - total_events: Number of events analyzed
        # - failed_attempts: Dict of username -> failure count
        # - brute_force_attempts: Detected attacks
        # - suspicious_usernames: Risky username attempts
        # - recommendations: Security recommendations
```

### Utility Functions

```python
def create_secure_passwords() -> bool:
    """Create and update secure passwords for all users."""

def generate_secure_users() -> bool:
    """Generate production users with security best practices."""

def run_security_analysis() -> Dict[str, any]:
    """Run complete security analysis and generate report."""

def verify_encryption_migration() -> Tuple[bool, List[str]]:
    """Verify Argon2id encryption migration status."""
```

## 📄 License

This module is part of the TalkBridge project and follows the same licensing terms.

## 🤝 Contributing

When contributing to authentication utilities:

1. **Follow security best practices**
2. **Add comprehensive tests**
3. **Update documentation**
4. **Security review required** for all changes
5. **Test with production-like data**

## 📞 Support

For issues related to authentication utilities:

1. Check this README for common solutions
2. Review the troubleshooting section
3. Enable debug logging for detailed output
4. Verify environment configuration
5. Test database connectivity

---

**⚠️ Security Notice**: These utilities handle sensitive authentication data. Always follow security best practices and test thoroughly in non-production environments before deployment.