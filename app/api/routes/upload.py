import os
import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from PIL import Image
import shutil

from app.api.deps import get_current_user, get_db
from app.models import User, Item
from app.config import settings

router = APIRouter()

# Allowed image extensions and max file size
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = settings.MAX_FILE_SIZE  # 5MB
MAX_IMAGE_DIMENSION = 2048  # Max width/height in pixels


def validate_image(file: UploadFile) -> None:
    """Validate uploaded image file"""
    
    # Check file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )


def process_image(file_path: str) -> str:
    """Process and optimize uploaded image"""
    try:
        # Open and process image
        with Image.open(file_path) as img:
            # Convert RGBA to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Resize if image is too large
            if img.width > MAX_IMAGE_DIMENSION or img.height > MAX_IMAGE_DIMENSION:
                img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(file_path, "JPEG", quality=85, optimize=True)
            
        return file_path
    except Exception as e:
        # Remove file if processing failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing image: {str(e)}"
        )


@router.post("/images")
def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Upload a single image
    """
    validate_image(file)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process and optimize image
        processed_path = process_image(file_path)
        
        # Return image URL
        image_url = f"/uploads/{unique_filename}"
        
        return {
            "message": "Image uploaded successfully",
            "image_url": image_url,
            "filename": unique_filename,
            "original_filename": file.filename
        }
        
    except Exception as e:
        # Clean up file if upload failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading image: {str(e)}"
        )
    finally:
        file.file.close()


@router.post("/images/multiple")
def upload_multiple_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Upload multiple images at once (max 5 images)
    """
    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 images allowed per upload"
        )
    
    uploaded_images = []
    failed_uploads = []
    
    for file in files:
        try:
            validate_image(file)
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
            
            # Save uploaded file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Process and optimize image
            process_image(file_path)
            
            # Add to successful uploads
            image_url = f"/uploads/{unique_filename}"
            uploaded_images.append({
                "image_url": image_url,
                "filename": unique_filename,
                "original_filename": file.filename
            })
            
        except Exception as e:
            failed_uploads.append({
                "filename": file.filename,
                "error": str(e)
            })
        finally:
            file.file.close()
    
    return {
        "message": f"Uploaded {len(uploaded_images)} images successfully",
        "uploaded_images": uploaded_images,
        "failed_uploads": failed_uploads,
        "total_uploaded": len(uploaded_images),
        "total_failed": len(failed_uploads)
    }


@router.post("/items/{item_id}/images")
def upload_item_images(
    item_id: int,
    files: List[UploadFile] = File(...),
    set_primary: int = Form(0, description="Index of image to set as primary (0-based)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Upload images for a specific item
    """
    # Verify item ownership
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.owner_id == current_user.id,
        Item.is_active == True
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found or you don't have permission to edit it"
        )
    
    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 images allowed per item"
        )
    
    # Upload images
    upload_result = upload_multiple_images(files, current_user)
    uploaded_images = upload_result["uploaded_images"]
    
    if not uploaded_images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No images were uploaded successfully"
        )
    
    # Update item with image URLs
    image_urls = [img["image_url"] for img in uploaded_images]
    
    # Add to existing images or replace
    if item.image_urls:
        item.image_urls.extend(image_urls)
    else:
        item.image_urls = image_urls
    
    # Set primary image
    if 0 <= set_primary < len(image_urls):
        item.primary_image_url = image_urls[set_primary]
    elif not item.primary_image_url and image_urls:
        # Set first image as primary if no primary is set
        item.primary_image_url = image_urls[0]
    
    db.commit()
    db.refresh(item)
    
    return {
        "message": f"Added {len(uploaded_images)} images to item '{item.title}'",
        "item_id": item.id,
        "uploaded_images": uploaded_images,
        "primary_image_url": item.primary_image_url,
        "total_images": len(item.image_urls) if item.image_urls else 0
    }


@router.delete("/items/{item_id}/images")
def remove_item_image(
    item_id: int,
    image_url: str = Form(..., description="Image URL to remove"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Remove an image from an item
    """
    # Verify item ownership
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.owner_id == current_user.id,
        Item.is_active == True
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found or you don't have permission to edit it"
        )
    
    if not item.image_urls or image_url not in item.image_urls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found for this item"
        )
    
    # Remove image URL from list
    item.image_urls.remove(image_url)
    
    # Update primary image if needed
    if item.primary_image_url == image_url:
        item.primary_image_url = item.image_urls[0] if item.image_urls else None
    
    # Delete physical file
    try:
        filename = image_url.split("/")[-1]
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Could not delete file {image_url}: {e}")
    
    db.commit()
    db.refresh(item)
    
    return {
        "message": "Image removed successfully",
        "item_id": item.id,
        "removed_image": image_url,
        "remaining_images": len(item.image_urls) if item.image_urls else 0
    }


@router.get("/images/{filename}")
def get_image(filename: str):
    """
    Serve uploaded images
    """
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return FileResponse(file_path)