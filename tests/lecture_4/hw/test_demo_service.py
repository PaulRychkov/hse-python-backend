import datetime
from datetime import timedelta
import pytest
from starlette.testclient import TestClient

from lecture_4.demo_service.api.contracts import *
from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.core.users import UserInfo, UserService, password_is_longer_than_8

app_instance = create_app()
client = TestClient(app_instance)

@pytest.fixture
def auth_request_fixture():
    return UserAuthRequest(
        username="user123",
        password=SecretStr("newPassword123")
    )

@pytest.fixture
def user_info_fixture():
    return UserInfo(
        username="user123",
        name="user11",
        birthdate=datetime.now(),
        role=UserRole.USER,
        password=SecretStr("newPassword123")
    )

@pytest.fixture
def registration_request_fixture():
    return RegisterUserRequest(
        username="user123",
        name="user11",
        birthdate=datetime.now(),
        password=SecretStr("newPassword123")
    )

@pytest.fixture
def user_response_fixture():
    return UserResponse(
        uid=1,
        username="user123",
        name="user11",
        birthdate=datetime.now(),
        role=UserRole.USER
    )

@pytest.fixture
def user_entity_fixture(user_info_fixture):
    return UserEntity(
        uid=1,
        info=user_info_fixture
    )

@pytest.fixture
def user_service_fixture():
    return UserService()

def test_app_initialization():
    assert app_instance is not None

def test_password_length_validator():
    assert not password_is_longer_than_8("short")
    assert password_is_longer_than_8("longlonglonglonglong")

def test_validate_user_role():
    current_role = UserRole.USER
    assert current_role == UserRole.USER

def test_validate_user_entity(user_entity_fixture):
    now = datetime.now()
    assert user_entity_fixture.uid == 1
    assert user_entity_fixture.info.username == "user123"
    assert user_entity_fixture.info.name == "user11"
    assert user_entity_fixture.info.birthdate - now < timedelta(seconds=1)
    assert user_entity_fixture.info.role == UserRole.USER
    assert user_entity_fixture.info.password == SecretStr("newPassword123")

def test_validate_registration_request(registration_request_fixture):
    now = datetime.now()
    assert registration_request_fixture.username == "user123"
    assert registration_request_fixture.name == "user11"
    assert registration_request_fixture.birthdate - now < timedelta(seconds=1)
    assert registration_request_fixture.password == SecretStr("newPassword123")

def test_validate_user_info(user_info_fixture):
    now = datetime.now()
    assert user_info_fixture.username == "user123"
    assert user_info_fixture.name == "user11"
    assert user_info_fixture.birthdate - now < timedelta(seconds=1)
    assert user_info_fixture.role == UserRole.USER
    assert user_info_fixture.password == SecretStr("newPassword123")

def test_user_service_operations(user_service_fixture, user_info_fixture):
    user_entity_obj = user_service_fixture.register(user_info_fixture)
    assert user_entity_obj.info.username == user_info_fixture.username
    assert user_entity_obj.info.name == user_info_fixture.name
    assert user_entity_obj.info.birthdate == user_info_fixture.birthdate
    assert user_entity_obj.info.role == user_info_fixture.role
    assert user_entity_obj.info.password == user_info_fixture.password

    assert user_service_fixture.get_by_username(user_info_fixture.username) == user_entity_obj
    assert user_service_fixture.get_by_id(user_entity_obj.uid) == user_entity_obj

    user_service_fixture.grant_admin(user_entity_obj.uid)
    assert user_entity_obj.info.role == UserRole.ADMIN

    with pytest.raises(ValueError):
        user_service_fixture.grant_admin(2)

def test_user_response_consistency(user_response_fixture, user_entity_fixture):
    now = datetime.now()

    assert user_response_fixture.uid == 1
    assert user_response_fixture.username == "user123"
    assert user_response_fixture.name == "user11"
    assert user_response_fixture.birthdate - now < timedelta(seconds=1)
    assert user_response_fixture.role == UserRole.USER

    response_from_entity = UserResponse.from_user_entity(user_entity_fixture)
    assert response_from_entity.uid == 1
    assert response_from_entity.username == "user123"
    assert response_from_entity.name == "user11"
    assert response_from_entity.birthdate - now < timedelta(seconds=1)
    assert response_from_entity.role == UserRole.USER

def test_validate_auth_request(auth_request_fixture):
    assert auth_request_fixture.username == "user123"
    assert auth_request_fixture.password == SecretStr("newPassword123")

@pytest.fixture
def test_client_fixture():
    with TestClient(create_app()) as test_client:
        yield test_client

def test_user_retrieval_endpoint(test_client_fixture, registration_request_fixture, user_entity_fixture, user_response_fixture):
    request_content = registration_request_fixture.model_dump()
    request_content['birthdate'] = request_content['birthdate'].isoformat()
    request_content['password'] = registration_request_fixture.password.get_secret_value()

    initial_response = test_client_fixture.post("/user-register", json=request_content)

    headers_for_auth = {
        "Authorization": "Basic dXNlcjEyMzpuZXdQYXNzd29yZDEyMw=="
    }

    response = test_client_fixture.post("/user-get", params={'id': initial_response.json().get("uid")},
                                        headers=headers_for_auth)

    assert response.status_code == 200
    assert response.json().get('name') == user_response_fixture.name
    assert response.json().get('username') == user_response_fixture.username
    assert response.json().get('role') == user_response_fixture.role
    assert datetime.fromisoformat(response.json().get('birthdate')) - user_response_fixture.birthdate < timedelta(seconds=1)

    response = test_client_fixture.post("/user-get", params={'id': user_entity_fixture.uid, 'username': user_entity_fixture.info.username})
    assert response.status_code == 401

    response = test_client_fixture.post("/user-get", params={'id': user_entity_fixture.uid, 'username': user_entity_fixture.info.username},
                                        headers=headers_for_auth)
    assert response.status_code == 400

    response = test_client_fixture.post("/user-get", params={}, headers=headers_for_auth)
    assert response.status_code == 400

    admin_request_content = {
        "username": "admin",
        "name": "admin",
        "birthdate": datetime.now().isoformat(),
        "password": "ultraSecret123"
    }
    headers_for_admin_auth = {
        "Authorization": "Basic YWRtaW46c3VwZXJTZWNyZXRBZG1pblBhc3N3b3JkMTIz"
    }
    test_client_fixture.post("/user-register", json=admin_request_content)
    response = test_client_fixture.post("/user-get", params={"username": "admin"}, headers=headers_for_admin_auth)
    assert response.status_code == 200

    test_client_fixture.post("/user-register", json=admin_request_content)
    response = test_client_fixture.post("/user-get", params={"username": "nonExistent"}, headers=headers_for_admin_auth)
    assert response.status_code == 404

    headers_for_bad_auth = {
        "Authorization": "Basic YWRtaW5Vc2VyOmJhZFBhc3M="
    }

    response = test_client_fixture.post("/user-get", params={'id': initial_response.json().get("uid")},
                                        headers=headers_for_bad_auth)
    assert response.status_code == 401

def test_user_registration_endpoint(test_client_fixture, registration_request_fixture, user_response_fixture):
    request_content = registration_request_fixture.model_dump()
    request_content['birthdate'] = request_content['birthdate'].isoformat()
    request_content['password'] = registration_request_fixture.password.get_secret_value()

    response = test_client_fixture.post("/user-register", json=request_content)

    assert response.status_code == 200
    assert response.json().get('name') == user_response_fixture.name
    assert response.json().get('username') == user_response_fixture.username
    assert response.json().get('role') == user_response_fixture.role
    assert datetime.fromisoformat(response.json().get('birthdate')) - user_response_fixture.birthdate < timedelta(seconds=1)
    
def test_user_promotion_endpoint(test_client_fixture, registration_request_fixture):
    """Ensures user promotion endpoint is functional."""
    admin_request_content = {
        "username": "admin",
        "name": "admin",
        "birthdate": datetime.now().isoformat(),
        "password": "ultraSecret123"
    }
    headers_for_admin_auth = {
        "Authorization": "Basic YWRtaW46c3VwZXJTZWNyZXRBZG1pblBhc3N3b3JkMTIz"
    }
    headers_for_regular_auth = {
        "Authorization": "Basic dXNlcjEyMzpuZXdQYXNzd29yZDEyMw=="
    }

    test_client_fixture.post("/user-register", json=admin_request_content)

    request_content = registration_request_fixture.model_dump()
    request_content['birthdate'] = request_content['birthdate'].isoformat()
    request_content['password'] = registration_request_fixture.password.get_secret_value()
    initial_response = test_client_fixture.post("/user-register", json=request_content)
    assert initial_response.status_code == 200

    response = test_client_fixture.post("/user-promote", params={'id': initial_response.json().get("uid")}, headers=headers_for_regular_auth)
    assert response.status_code == 403

    response = test_client_fixture.post("/user-promote", params={'id': initial_response.json().get("uid")}, headers=headers_for_admin_auth)
    assert response.status_code == 200

    invalid_admin_request_content = {
        "username": "admin123",
        "name": "admin123",
        "birthdate": datetime.now().isoformat(),
        "password": ""
    }

    response = test_client_fixture.post("/user-register", json=invalid_admin_request_content)
    assert response.status_code == 400