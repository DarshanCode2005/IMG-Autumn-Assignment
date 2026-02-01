from celery import shared_task
from django.conf import settings
from .models import Photo, TaggedIn
from social.models import Like
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
from pathlib import Path
import json
import os
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Initialize ResNet Model once
try:
    _resnet_model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
    _resnet_model.eval()
except Exception as e:
    print(f"Warning: Failed to load ResNet model: {e}")
    _resnet_model = None

# Labels lazy loader
_imagenet_labels = None
def get_imagenet_labels():
    global _imagenet_labels
    if _imagenet_labels is None:
        try:
            import urllib.request
            url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
            filename = "imagenet_classes.txt"
            if not os.path.exists(filename):
                urllib.request.urlretrieve(url, filename)
            with open(filename, "r") as f:
                _imagenet_labels = [line.strip() for line in f.readlines()]
        except:
            _imagenet_labels = []
    return _imagenet_labels

@shared_task
def process_photo_task(photo_id, original_path):
    print(f"Processing photo {photo_id} at {original_path}")
    try:
        photo = Photo.objects.get(id=photo_id)
        photo.processing_status = 'processing'
        photo.save()
        
        # Paths
        original_file = Path(original_path)
        media_root = Path(settings.MEDIA_ROOT)
        
        # Ensure directories exist
        (media_root / "photos/thumbnails").mkdir(parents=True, exist_ok=True)
        (media_root / "photos/watermarked").mkdir(parents=True, exist_ok=True)

        thumbnail_path = f"photos/thumbnails/thumb_{original_file.name}"
        watermarked_path = f"photos/watermarked/water_{original_file.name}"
        
        full_thumb_path = media_root / thumbnail_path
        full_water_path = media_root / watermarked_path

        # 1. EXIF Data
        exif_data = {}
        with Image.open(original_file) as img:
            if hasattr(img, 'getexif'):
                exif = img.getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[str(tag)] = str(value)
        photo.exif_data = exif_data

        # 2. Thumbnail
        with Image.open(original_file) as img:
             if img.mode != 'RGB':
                img = img.convert('RGB')
             img.thumbnail((400, 400), Image.Resampling.LANCZOS)
             img.save(full_thumb_path, "JPEG", quality=85)
        photo.thumbnail_image = str(thumbnail_path)

        # 3. Watermark
        with Image.open(original_file) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            draw = ImageDraw.Draw(img)
            # Simple text watermark for now
            text = "IMG Project"
            font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=font)
            textwidth = bbox[2] - bbox[0]
            textheight = bbox[3] - bbox[1]
            x = img.width - textwidth - 10
            y = img.height - textheight - 10
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 128))
            img.save(full_water_path, "JPEG", quality=95)
        photo.watermarked_image = str(watermarked_path)

        # 4. AI Tagging
        if _resnet_model:
            with Image.open(original_file) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                preprocess = transforms.Compose([
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                ])
                input_tensor = preprocess(img)
                input_batch = input_tensor.unsqueeze(0)

                with torch.no_grad():
                    output = _resnet_model(input_batch)
                
                probabilities = torch.nn.functional.softmax(output[0], dim=0)
                top5_prob, top5_catid = torch.topk(probabilities, 5)
                
                labels = get_imagenet_labels()
                if labels:
                    tags = [labels[idx.item()] for idx in top5_catid]
                    photo.ai_tags = tags

        photo.processing_status = 'completed'
        photo.save()
        
        # Notify Uploader (optional - gracefully handle if channels not available)
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"user_{photo.uploader.id}",
                    {
                        "type": "notification_message",
                        "message": {
                            "type": "photo_processed",
                            "photo_id": photo.id,
                            "status": "completed",
                            "thumbnail_url": photo.thumbnail_image.url if photo.thumbnail_image else None
                        }
                    }
                )
        except Exception as notify_error:
            print(f"Could not send notification (WebSocket not available): {notify_error}")

    except Exception as e:
        print(f"Error processing photo: {e}")
        try:
            photo.processing_status = 'failed'
            photo.save()
        except:
            pass
    
    return True
