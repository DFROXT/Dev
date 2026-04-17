import json
from drive_handler import read_file, upload_file, list_files

LEARNING_FILE_ID = None  # will set after first upload

def load_knowledge():
    """Load existing Q&A pairs from Drive"""
    global LEARNING_FILE_ID
    files = list_files("name='ai_memory.json'")
    if files:
        LEARNING_FILE_ID = files[0]['id']
        content = read_file(LEARNING_FILE_ID)
        return json.loads(content)
    return {"qa": []}  # empty

def save_knowledge(data):
    """Save Q&A back to Drive"""
    content = json.dumps(data, indent=2)
    # Write to temp file then upload
    with open("/tmp/ai_memory.json", "w") as f:
        f.write(content)
    if LEARNING_FILE_ID:
        # Update existing file (delete and re-upload for simplicity)
        service = get_drive_service()
        service.files().delete(fileId=LEARNING_FILE_ID).execute()
    new_id = upload_file("/tmp/ai_memory.json")
    global LEARNING_FILE_ID
    LEARNING_FILE_ID = new_id

def learn_from_conversation(user_msg, ai_response, user_rating=None):
    """Store interaction for future reference"""
    knowledge = load_knowledge()
    knowledge["qa"].append({
        "question": user_msg,
        "answer": ai_response,
        "rating": user_rating,
        "timestamp": str(datetime.now())
    })
    # Keep only last 5000 to avoid size issues
    if len(knowledge["qa"]) > 5000:
        knowledge["qa"] = knowledge["qa"][-5000:]
    save_knowledge(knowledge)
