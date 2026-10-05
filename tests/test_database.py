import pytest
from app.database.database import (
    create_user,
    create_document,
    create_conversation,
    save_message,
    get_conversation_history,
    get_company_profile,
    update_company_profile
)


@pytest.mark.offline
def test_database_lifecycle():
    user_id = create_user()
    assert user_id

    doc_id = create_document(user_id=user_id, filename="doc.pdf")
    assert doc_id

    conv_id = create_conversation(user_id=user_id, document_id=doc_id)
    assert conv_id

    save_message(conv_id, "user", "Hello")
    save_message(conv_id, "assistant", "World")

    history = get_conversation_history(conv_id)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert "id" in history[0]


@pytest.mark.offline
def test_company_profile():
    prof = get_company_profile()
    assert "company_name" in prof

    update_company_profile(company_name="ACME Corp", vat_number="IT12345678901")
    updated = get_company_profile()
    assert updated["company_name"] == "ACME Corp"
    assert updated["vat_number"] == "IT12345678901"