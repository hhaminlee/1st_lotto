"""
Firebase 클라이언트 모듈
Firebase 초기화 및 Firestore 클라이언트 관리
"""

import os
from typing import Optional, Any

import firebase_admin
from firebase_admin import credentials, firestore


_firestore_client: Optional[Any] = None


def initialize_firebase(use_env: bool = True) -> Optional[Any]:
    """
    Firebase를 초기화합니다.

    Args:
        use_env: 환경변수에서 설정을 가져올지 여부 (False면 Firebase 자동 인증)

    Returns:
        Firestore 클라이언트 또는 실패 시 None
    """
    global _firestore_client

    try:
        # 이미 초기화되어 있으면 기존 클라이언트 반환
        if firebase_admin._apps:
            _firestore_client = firestore.client()
            return _firestore_client

        if use_env:
            # 환경변수에서 Firebase 설정 가져오기
            firebase_config = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace(
                    "\\n", "\n"
                ),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": os.getenv(
                    "FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"
                ),
                "token_uri": os.getenv(
                    "FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"
                ),
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
            }

            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
        else:
            # Firebase Functions 환경에서는 자동 인증
            firebase_admin.initialize_app()

        _firestore_client = firestore.client()
        return _firestore_client

    except Exception as e:
        print(f"Firebase 초기화 실패: {e}")
        return None


def get_firestore_client() -> Optional[Any]:
    """
    Firestore 클라이언트를 반환합니다.
    초기화되지 않았으면 초기화를 시도합니다.

    Returns:
        Firestore 클라이언트 또는 None
    """
    global _firestore_client

    if _firestore_client is None:
        return initialize_firebase()

    return _firestore_client


def get_firestore_client_for_functions() -> Optional[Any]:
    """
    Firebase Functions 환경용 Firestore 클라이언트를 반환합니다.

    Returns:
        Firestore 클라이언트 또는 None
    """
    global _firestore_client

    if _firestore_client is None:
        return initialize_firebase(use_env=False)

    return _firestore_client
