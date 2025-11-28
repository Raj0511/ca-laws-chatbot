from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.api import deps
from app.models.user import User
from app.models.knowledge import DocumentItem
from app.services.file_service import extract_text_from_pdf
# Import the new simplified function
from app.services.vector_service import add_document_to_knowledge_base 

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user)
):
    if file.content_type != "application/pdf":
        raise HTTPException(400, detail="Only PDF files are supported.")

    try:
        # 1. Extract Text
        content = await file.read()
        text_content = await extract_text_from_pdf(content)
        
        if not text_content.strip():
            raise HTTPException(400, detail="Empty PDF")

        # 2. Add to LangChain/FAISS Index
        add_document_to_knowledge_base(text_content)

        # 3. Save Record to Mongo (Just for record-keeping)
        doc = DocumentItem(
            user_id=current_user.id,
            filename=file.filename,
            file_type=file.content_type,
            file_size=len(content),
            content="[Content Indexed in FAISS]", # Save space in Mongo
            status="indexed"
        )
        await doc.insert()

        return {"status": "success", "filename": file.filename}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(500, detail=str(e))