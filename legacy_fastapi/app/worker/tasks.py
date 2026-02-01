import os
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
from app.worker.celery_app import celery_app
from app.core.database import SessionLocal
from app.crud.photo import update_photo_processing


def extract_exif_data(image_path: str) -> dict:
    """Extract EXIF data from image using Pillow."""
    exif_data = {}
    try:
        with Image.open(image_path) as img:
            # Try new method first (Pillow >= 8.0)
            if hasattr(img, 'getexif'):
                exif = img.getexif()
                if exif is not None:
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        # Convert non-serializable types to strings
                        try:
                            json.dumps(value)
                            exif_data[tag] = value
                        except (TypeError, ValueError):
                            exif_data[tag] = str(value)
            # Fallback to old method (Pillow < 8.0)
            elif hasattr(img, '_getexif') and img._getexif() is not None:
                exif = img._getexif()
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    try:
                        json.dumps(value)
                        exif_data[tag] = value
                    except (TypeError, ValueError):
                        exif_data[tag] = str(value)
    except Exception as e:
        print(f"Error extracting EXIF data: {e}")
    return exif_data


def generate_thumbnail(image_path: str, output_path: str, size: tuple = (400, 400)) -> str:
    """Generate a 400x400 thumbnail from the original image."""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (JPEG doesn't support RGBA)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            # Maintain aspect ratio
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(output_path, "JPEG", quality=85)
        return output_path
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        raise


def apply_watermark(image_path: str, output_path: str, watermark_text: str = "IMG Project") -> str:
    """Apply text watermark overlay to image."""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create a copy for watermarking
            watermarked = img.copy()
            draw = ImageDraw.Draw(watermarked)
            
            # Try to load a font, fallback to default if not available
            try:
                # Try to use a system font
                font_size = max(20, int(img.width / 30))
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # Calculate text position (bottom right corner)
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Position with padding
            padding = 10
            x = img.width - text_width - padding
            y = img.height - text_height - padding
            
            # Draw semi-transparent background for text
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                fill=(0, 0, 0, 128)
            )
            watermarked = Image.alpha_composite(
                watermarked.convert('RGBA'),
                overlay
            ).convert('RGB')
            
            # Draw text
            draw = ImageDraw.Draw(watermarked)
            draw.text((x, y), watermark_text, fill=(255, 255, 255), font=font)
            
            watermarked.save(output_path, "JPEG", quality=95)
        return output_path
    except Exception as e:
        print(f"Error applying watermark: {e}")
        raise


def load_resnet_model():
    """Load pre-trained ResNet50 model."""
    try:
        model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
        model.eval()
        return model
    except Exception as e:
        print(f"Error loading ResNet model: {e}")
        return None


# Load model once at module level
_resnet_model = None
_imagenet_labels = None


def get_imagenet_labels():
    """Get ImageNet class labels."""
    global _imagenet_labels
    if _imagenet_labels is None:
        try:
            import urllib.request
            url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
            urllib.request.urlretrieve(url, "imagenet_classes.txt")
            with open("imagenet_classes.txt", "r") as f:
                _imagenet_labels = [line.strip() for line in f.readlines()]
        except Exception as e:
            print(f"Error loading ImageNet labels: {e}")
            # Fallback to generic labels
            _imagenet_labels = [f"class_{i}" for i in range(1000)]
    return _imagenet_labels


def generate_ai_tags(image_path: str, top_k: int = 5) -> list:
    """Generate descriptive tags using ResNet50 model."""
    global _resnet_model
    
    if _resnet_model is None:
        _resnet_model = load_resnet_model()
    
    if _resnet_model is None:
        return []
    
    try:
        # Preprocess image
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_tensor = transform(img).unsqueeze(0)
        
        # Get predictions
        with torch.no_grad():
            outputs = _resnet_model(img_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            top_probs, top_indices = torch.topk(probabilities, top_k)
        
        # Get labels
        labels = get_imagenet_labels()
        tags = []
        for prob, idx in zip(top_probs, top_indices):
            label = labels[idx.item()]
            # Format label (remove underscores, capitalize)
            formatted_label = label.replace("_", " ").title()
            tags.append(formatted_label)
        
        return tags
    except Exception as e:
        print(f"Error generating AI tags: {e}")
        return []


@celery_app.task(name="process_photo")
def process_photo_task(photo_id: int, original_path: str):
    """
    Celery task to process uploaded photo.
    """
    print(f"DEBUG: Celery process_photo_task STARTED for photo_id: {photo_id}")
    db = SessionLocal()
    
    try:
        # Update status to processing
        update_photo_processing(db, photo_id, processing_status="processing")
        
        # Setup paths
        original_file = Path(original_path)
        media_dir = Path("media")
        thumbnails_dir = media_dir / "thumbnails"
        watermarked_dir = media_dir / "watermarked"
        
        thumbnails_dir.mkdir(parents=True, exist_ok=True)
        watermarked_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate thumbnail filename
        thumbnail_filename = f"thumb_{original_file.stem}.jpg"
        thumbnail_path = thumbnails_dir / thumbnail_filename
        
        # Generate watermarked filename
        watermarked_filename = f"watermarked_{original_file.stem}.jpg"
        watermarked_path = watermarked_dir / watermarked_filename
        
        # 1. Extract EXIF data
        exif_data = extract_exif_data(original_path)
        
        # 2. Generate thumbnail
        generate_thumbnail(original_path, str(thumbnail_path))
        
        # 3. Apply watermark
        apply_watermark(original_path, str(watermarked_path))
        
        # 4. Generate AI tags
        ai_tags = generate_ai_tags(original_path)
        
        # Update photo record with processing results
        update_photo_processing(
            db=db,
            photo_id=photo_id,
            thumbnail_path=str(thumbnail_path).replace("\\", "/"),
            watermarked_path=str(watermarked_path).replace("\\", "/"),
            exif_data=exif_data,
            ai_tags=ai_tags,
            processing_status="completed"
        )
        
        # Get photo and uploader info for notification
        from app.models.models import Photo, TaggedIn
        photo = db.query(Photo).filter(Photo.id == photo_id).first()
        
        # Broadcast notification to uploader and tagged users
        if photo:
            uploader_id = photo.uploader_id
            
            # Get tagged users
            tagged_users = db.query(TaggedIn).filter(TaggedIn.photo_id == photo_id).all()
            tagged_user_ids = [tag.user_id for tag in tagged_users]
            
            # Broadcast notification using helper function
            from app.websockets.broadcast import broadcast_photo_processed
            broadcast_photo_processed(
                photo_id=photo_id,
                uploader_id=uploader_id,
                tagged_user_ids=tagged_user_ids,
                thumbnail_path=str(thumbnail_path).replace("\\", "/"),
                status="completed"
            )
        
        return {
            "photo_id": photo_id,
            "status": "completed",
            "thumbnail_path": str(thumbnail_path).replace("\\", "/"),
            "exif_data": exif_data,
            "ai_tags": ai_tags
        }
        
    except Exception as e:
        # Update status to failed
        update_photo_processing(db, photo_id, processing_status="failed")
        
        # Notify uploader of failure
        from app.models.models import Photo
        photo = db.query(Photo).filter(Photo.id == photo_id).first()
        if photo:
            from app.websockets.broadcast import broadcast_photo_processed
            broadcast_photo_processed(
                photo_id=photo_id,
                uploader_id=photo.uploader_id,
                tagged_user_ids=[],
                thumbnail_path=None,
                status="failed"
            )
        
        print(f"Error processing photo {photo_id}: {e}")
        raise
    finally:
        db.close()

