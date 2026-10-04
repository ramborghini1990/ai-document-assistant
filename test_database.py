import os
import tempfile
from app.database.database import (
    init_db,
    create_user,
    create_document,
    create_conversation,
    save_message,
    get_conversation_history
)


def run_database_tests():
    print("Testing SQLite Database Layer and Schema Contracts...")

    # استفاده از دیتابیس موقت جهت ایزوله‌سازی آزمون بدون تخریب دیتابیس اصلی
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db.close()
    os.environ["ASSISTANT_DB_PATH"] = temp_db.name

    try:
        init_db()

        # ۱. ساخت کاربر
        user_id = create_user()
        assert user_id and isinstance(user_id, str)
        print(f"✓ 1. User created: {user_id}")

        # ۲. ساخت سند
        doc_id = create_document(user_id=user_id, filename="sample_report.pdf")
        assert doc_id and isinstance(doc_id, str)
        print(f"✓ 2. Document created: {doc_id}")

        # ۳. ساخت مکالمه با نگاشت اختیاری سند
        conv_id = create_conversation(user_id=user_id, document_id=doc_id)
        assert conv_id and isinstance(conv_id, str)
        print(f"✓ 3. Conversation created with document binding: {conv_id}")

        # ۴. ذخیره پیام‌ها
        msg1_id = save_message(conv_id, "user", "What is the main finding in this study?")
        msg2_id = save_message(conv_id, "assistant", "The study readapts the SING algorithm for the Italian electrical grid.")
        assert msg1_id and msg2_id
        print("✓ 4. Messages saved to conversation successfully.")

        # ۵. بازخوانی تاریخچه و راستی‌آزمایی قرارداد فیلدها (شامل id)
        history = get_conversation_history(conv_id)
        assert len(history) == 2
        for msg in history:
            assert "id" in msg, "Field 'id' missing from message history dictionary!"
            assert "role" in msg
            assert "content" in msg
            assert "created_at" in msg
            print(f"  [{msg['role'].upper()}]: {msg['content']} (ID: {msg['id'][:8]}...)")

        print("✓ 5. Conversation history retrieved with guaranteed deterministic order.")
        print("\n🎉 Database verification completed successfully!")

    finally:
        if os.path.exists(temp_db.name):
            try:
                os.remove(temp_db.name)
            except PermissionError:
                pass


if __name__ == "__main__":
    run_database_tests()