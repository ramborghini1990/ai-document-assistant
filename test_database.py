from app.database.database import (
    init_db,
    create_user,
    create_document,
    create_conversation,
    save_message,
    get_conversation_history
)

if __name__ == "__main__":
    print("Initializing SQLite Database...")
    init_db()

    print("\n1. Creating test User...")
    user_id = create_user()
    print(f"User created: {user_id}")

    print("\n2. Creating test Document record...")
    doc_id = create_document(user_id=user_id, filename="sample_report.pdf")
    print(f"Document created: {doc_id}")

    print("\n3. Creating Conversation session...")
    conv_id = create_conversation(user_id=user_id, document_id=doc_id)
    print(f"Conversation created: {conv_id}")

    print("\n4. Saving Messages to Conversation...")
    save_message(conv_id, "user", "What is the main finding in this study?")
    save_message(conv_id, "assistant", "The study readapts the SING algorithm for the Italian electrical grid.")

    print("\n5. Retrieving Conversation History:")
    history = get_conversation_history(conv_id)
    for msg in history:
        print(f"[{msg['role'].upper()}]: {msg['content']} (ID: {msg['id'][:8]}...)")

    print("\nDatabase verification completed successfully!")