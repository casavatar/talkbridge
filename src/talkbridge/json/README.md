# TalkBridge User Management System

This directory contains the secure user management system for TalkBridge with enhanced security features.

## 🔐 Security Features

### Enhanced Password Security
- **Salted Password Hashing**: Each user has a unique 32-character salt
- **Cryptographically Secure**: Uses `secrets` module for random generation
- **SHA-256 Hashing**: Passwords are hashed with salt using SHA-256
- **Backward Compatibility**: Supports legacy password hashes

### Account Protection
- **Account Locking**: Accounts locked after 5 failed login attempts
- **Login Tracking**: Monitors failed attempts and last login times
- **Password Change Enforcement**: Forces password change on first login
- **Session Timeouts**: Role-based session timeout limits

### User Roles & Permissions

#### 🔴 Admin
- **Security Level**: High
- **Session Timeout**: 3600 seconds (1 hour)
- **Permissions**:
  - User management
  - System settings
  - View logs
  - Unlock accounts
  - Create/delete users
  - Modify roles

#### 🟡 Moderator
- **Security Level**: Medium
- **Session Timeout**: 2400 seconds (40 minutes)
- **Permissions**:
  - Voice chat & translation
  - Avatar control
  - Chat history
  - Moderate chat
  - View user activity
  - Unlock user accounts

#### 🟢 User
- **Security Level**: Medium
- **Session Timeout**: 1800 seconds (30 minutes)
- **Permissions**:
  - Voice chat
  - Translation
  - Avatar control
  - Chat history
  - Personal settings

#### 🔵 Translator
- **Security Level**: Medium
- **Session Timeout**: 2400 seconds (40 minutes)
- **Permissions**:
  - All user permissions
  - Advanced translation
  - Translation history
  - Language management

#### 🟣 Developer
- **Security Level**: High
- **Session Timeout**: 7200 seconds (2 hours)
- **Permissions**:
  - All user permissions
  - System settings
  - View logs
  - Debug mode
  - API access
  - Development tools

#### 🟠 Analyst
- **Security Level**: Medium
- **Session Timeout**: 3600 seconds (1 hour)
- **Permissions**:
  - All user permissions
  - View analytics
  - Export data
  - View user activity
  - Translation analytics

#### 🔶 Support
- **Security Level**: Medium
- **Session Timeout**: 2400 seconds (40 minutes)
- **Permissions**:
  - All user permissions
  - View user activity
  - Unlock user accounts
  - Reset user passwords
  - View support tickets

#### ⚪ Guest
- **Security Level**: Low
- **Session Timeout**: 900 seconds (15 minutes)
- **Permissions**:
  - Voice chat
  - Translation
  - Avatar control
  - Personal settings

## 📁 Files

### `users.json`
The main user database file containing all user accounts with enhanced security features.

### `generate_secure_users.py`
Script to generate secure passwords and hashes for the users.json file.

### `passwords_dev_only.txt`
Development-only file containing generated passwords (DELETE IN PRODUCTION).

## 🚀 Usage

### Generate New Users
```bash
cd src/json
python generate_secure_users.py
```

This will:
1. Generate cryptographically secure passwords
2. Create unique salts for each user
3. Hash passwords with salt
4. Save to `users.json`
5. Create `passwords_dev_only.txt` with plain passwords

### Default Users Created
- `admin` - System administrator
- `user` - Regular user
- `moderator` - Chat moderator
- `guest` - Limited access user
- `translator` - Translation specialist
- `developer` - System developer
- `analyst` - Data analyst
- `support` - Support staff
- `test_user` - Testing account
- `demo_user` - Demonstration account

## 🔒 Security Best Practices

### Development Environment
1. Run `generate_secure_users.py` to create secure users
2. Use passwords from `passwords_dev_only.txt` for testing
3. **DELETE** `passwords_dev_only.txt` before production

### Production Environment
1. **NEVER** commit `passwords_dev_only.txt` to version control
2. Change all default passwords immediately
3. Enable two-factor authentication for admin accounts
4. Regularly rotate passwords
5. Monitor failed login attempts

### Password Requirements
- **Admin/Developer**: 20 characters minimum
- **Other Users**: 16 characters minimum
- **Character Set**: Letters, digits, symbols
- **Cryptographically Secure**: Generated using `secrets` module

## 🔧 Authentication Flow

1. **User Login Attempt**
   - Check if user exists
   - Check if account is locked
   - Verify password (salted or legacy)
   - Update login success/failure tracking

2. **Password Verification**
   - Check if user has salt (new system)
   - Use salted verification if available
   - Fall back to legacy verification
   - Lock account after 5 failures

3. **Security Updates**
   - Track last login time
   - Reset failed attempt counter
   - Update password change requirements

## 🛡️ Security Features

### Account Protection
- **Brute Force Protection**: Account locking after failed attempts
- **Session Management**: Role-based session timeouts
- **Password Policies**: Enforced password changes
- **Audit Trail**: Comprehensive login tracking

### Data Security
- **Salted Hashing**: Unique salt per user
- **Cryptographic Random**: Secure password generation
- **Backward Compatibility**: Legacy password support
- **Secure Storage**: JSON with proper permissions

### Monitoring
- **Failed Login Tracking**: Monitor suspicious activity
- **Account Locking**: Automatic protection
- **Login History**: Track user activity
- **Security Logging**: Comprehensive audit trail

## ⚠️ Important Notes

1. **Default Passwords**: All users require password change on first login
2. **Account Locking**: Enabled after 5 failed attempts
3. **Session Timeouts**: Vary by role and security level
4. **Development Mode**: Set `TALKBRIDGE_DEV_MODE=true` to see generated passwords
5. **Production Security**: Delete password files and change all defaults

## 🔄 Migration

The system supports both old and new password formats:
- **New Users**: Get salted password hashing
- **Legacy Users**: Continue working with old hashes
- **Automatic Detection**: System detects and handles both formats
- **Gradual Upgrade**: Users can be migrated over time 