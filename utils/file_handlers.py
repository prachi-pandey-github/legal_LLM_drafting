"""
File handling utilities for document management
"""
import os
import tempfile
import shutil
import logging
from typing import Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

def cleanup_temp_file(filepath: str):
    """Clean up temporary file"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.debug(f"Cleaned up temp file: {filepath}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temp file {filepath}: {str(e)}")

def generate_filename(document_type: str, extension: str = "docx") -> str:
    """Generate a filename for a document"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    safe_type = document_type.replace(" ", "_").lower()
    
    return f"{safe_type}_{timestamp}_{unique_id}.{extension}"

def ensure_directory(directory: str):
    """Ensure directory exists, create if it doesn't"""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Created directory: {directory}")

def save_document(content: bytes, filename: str, directory: str = "generated_documents") -> str:
    """Save document content to file"""
    try:
        ensure_directory(directory)
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'wb') as f:
            f.write(content)
        
        logger.info(f"Document saved: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Failed to save document: {str(e)}")
        raise

def read_document(filepath: str) -> Optional[bytes]:
    """Read document content from file"""
    try:
        with open(filepath, 'rb') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read document {filepath}: {str(e)}")
        return None

def list_documents(directory: str = "generated_documents", 
                  document_type: Optional[str] = None) -> list:
    """List documents in directory, optionally filtered by type"""
    if not os.path.exists(directory):
        return []
    
    files = []
    for filename in os.listdir(directory):
        if document_type and not filename.startswith(document_type):
            continue
        
        if filename.endswith('.docx'):
            filepath = os.path.join(directory, filename)
            stats = os.stat(filepath)
            
            files.append({
                "filename": filename,
                "path": filepath,
                "size": stats.st_size,
                "created": datetime.fromtimestamp(stats.st_ctime),
                "modified": datetime.fromtimestamp(stats.st_mtime)
            })
    
    # Sort by creation time (newest first)
    files.sort(key=lambda x: x["created"], reverse=True)
    return files

def cleanup_old_files(directory: str, max_age_hours: int = 24):
    """Clean up files older than specified hours"""
    if not os.path.exists(directory):
        return
    
    current_time = datetime.now()
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        try:
            if os.path.isfile(filepath):
                file_age = current_time - datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_age.total_seconds() > (max_age_hours * 3600):
                    os.remove(filepath)
                    logger.info(f"Cleaned up old file: {filepath}")
                    
        except Exception as e:
            logger.warning(f"Failed to cleanup file {filepath}: {str(e)}")

def get_file_info(filepath: str) -> Optional[dict]:
    """Get information about a file"""
    if not os.path.exists(filepath):
        return None
    
    try:
        stats = os.stat(filepath)
        
        return {
            "filename": os.path.basename(filepath),
            "path": filepath,
            "size": stats.st_size,
            "size_human": _format_size(stats.st_size),
            "created": datetime.fromtimestamp(stats.st_ctime),
            "modified": datetime.fromtimestamp(stats.st_mtime),
            "extension": os.path.splitext(filepath)[1].lower(),
            "type": _get_file_type(filepath)
        }
    except Exception as e:
        logger.error(f"Failed to get file info for {filepath}: {str(e)}")
        return None

def _format_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def _get_file_type(filepath: str) -> str:
    """Get file type based on extension"""
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.docx':
        return 'document'
    elif ext == '.pdf':
        return 'pdf'
    elif ext in ['.txt', '.md']:
        return 'text'
    elif ext in ['.json', '.xml', '.yaml', '.yml']:
        return 'data'
    else:
        return 'other'