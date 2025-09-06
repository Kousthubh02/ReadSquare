# ReadSquare API Testing Guide

## 🚀 Automated Testing with GitHub Actions

The GitHub Actions workflow automatically tests the API on every push and pull request. The workflow includes:

### ✅ What Gets Tested

1. **Django System Checks**: Validates Django configuration
2. **Database Migrations**: Ensures migrations are up-to-date
3. **API Endpoint Tests**: Tests all authentication and user management endpoints
4. **JWT Token Generation**: Verifies JWT authentication works
5. **Database Operations**: Tests user creation, login, profile access
6. **Security Checks**: Runs Django security checks
7. **Code Quality**: Linting with flake8, black, and isort

### 🔧 Test Configuration

The workflow uses:
- **PostgreSQL 14** as test database
- **Python 3.11** runtime
- **Coverage reporting** with codecov
- **Parallel test execution** for faster results

## 🧪 Manual Testing

### Quick API Test
```bash
# Install dependencies
pip install -r requirements.txt

# Run Django server
python manage.py runserver

# In another terminal, run manual tests
python test_api_manual.py
```

### Comprehensive Testing
```bash
# Run all Django tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Creates htmlcov/index.html

# Run specific test file
python manage.py test api.test_api

# Run with pytest (alternative)
pytest api/test_api.py -v
```

## 📋 Test Coverage

### Authentication Endpoints
- ✅ User registration with validation
- ✅ User login with JWT tokens
- ✅ Email verification workflow
- ✅ Password reset functionality
- ✅ Profile access with authentication

### Error Handling
- ✅ Invalid credentials
- ✅ Duplicate email registration
- ✅ Password mismatch validation
- ✅ Unauthorized access attempts
- ✅ Missing required fields

### Security Testing
- ✅ JWT token validation
- ✅ Authentication required endpoints
- ✅ CORS configuration
- ✅ Password hashing verification

## 🛠️ Testing Tools

### 1. Django Test Framework
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test api

# Run with verbosity
python manage.py test --verbosity=2
```

### 2. pytest (Alternative)
```bash
# Install pytest
pip install pytest pytest-django

# Run tests
pytest

# Run with coverage
pytest --cov=api
```

### 3. Manual API Testing Script
```bash
# Test against local server
python test_api_manual.py

# Test against custom URL
python test_api_manual.py http://yourdomain.com
```

### 4. Postman/Thunder Client
Import the API endpoints from `API_DOCUMENTATION.md` into your preferred API testing tool.

## 🔍 Debugging Tests

### View Test Output
```bash
# Detailed test output
python manage.py test --verbosity=2 --debug-mode

# Keep test database for inspection
python manage.py test --keepdb

# Run specific test method
python manage.py test api.test_api.UserAuthenticationAPITest.test_user_registration
```

### Common Issues

1. **Migration Errors**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **JWT Token Issues**
   - Check SIMPLE_JWT settings in settings.py
   - Verify AUTH_USER_MODEL is set correctly

3. **Database Connection**
   - Ensure PostgreSQL is running for CI tests
   - SQLite is used for local development

## 📊 CI/CD Pipeline

### Trigger Conditions
- Push to any branch (except main)
- Pull requests (except to main)

### Pipeline Steps
1. **Setup Environment**
   - PostgreSQL service
   - Python 3.11
   - Install dependencies

2. **Code Quality**
   - Black formatting check
   - isort import sorting
   - flake8 linting

3. **Django Tests**
   - System checks
   - Migration verification
   - Unit tests
   - Integration tests

4. **API Testing**
   - Endpoint accessibility
   - Authentication flow
   - JWT token generation
   - Error handling

5. **Security & Performance**
   - Django security checks
   - Coverage reporting
   - Performance benchmarks

### View Results
- Check the **Actions** tab in GitHub
- Coverage reports uploaded to Codecov
- Failed tests show detailed error messages

## 🎯 Adding New Tests

### For New API Endpoints
1. Add test methods to `api/test_api.py`
2. Follow naming convention: `test_endpoint_functionality`
3. Test both success and error cases
4. Include authentication tests where needed

### Example Test Structure
```python
def test_new_endpoint(self):
    """Test description"""
    # Setup
    data = {'key': 'value'}
    
    # Execute
    response = self.client.post('/api/new-endpoint/', data, format='json')
    
    # Assert
    self.assertEqual(response.status_code, 200)
    self.assertIn('expected_key', response.data)
```

## 🚨 Monitoring & Alerts

- Failed CI builds send notifications
- Coverage drops are reported
- Security issues are flagged
- Performance regressions are detected

## 📈 Performance Testing

```bash
# Load testing with Django
python manage.py test --parallel

# Memory usage profiling
python -m memory_profiler manage.py test

# Database query analysis
python manage.py test --debug-sql
```

---

**Happy Testing! 🎉**

For questions or issues, check the GitHub Actions logs or create an issue in the repository.
