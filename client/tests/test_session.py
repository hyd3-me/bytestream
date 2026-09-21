from client.keystore import session


def test_unlock_session_exists():
    assert hasattr(session, "unlock_session")
    assert callable(session.unlock_session)
