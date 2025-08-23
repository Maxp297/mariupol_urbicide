#!/usr/bin/env python3
"""
Asset Processing Pipeline for Mariupol Administrative Violence Documentation Project
Handles automatic processing, logging, and validation of various incoming files.
"""

import os
import sys
import hashlib
import yaml
import json
import shutil
import datetime
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
from config import PROJECT_ROOT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("asset_processing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("asset_processor")

# Constants
PROJECT_ROOT = Path(PROJECT_ROOT)
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
METADATA_DIR = PROJECT_ROOT / "data" / "metadata"
VIDEO_LOGS_DIR = PROJECT_ROOT / "data" / "video_logs"

# Ensure directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, METADATA_DIR, VIDEO_LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

class AssetProcessor:
    """Base class for all asset processors with common functionality"""
    
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self.original_filename = self.file_path.name
        self.file_extension = self.file_path.suffix.lower()
        self.metadata = self._initialize_metadata()
        
    def _initialize_metadata(self) -> Dict:
        """Initialize metadata dictionary with common fields"""
        return {
            "filename": self.original_filename,
            "file_extension": self.file_extension,
            "original_path": str(self.file_path),
            "file_size_bytes": self.file_path.stat().st_size,
            "date_added": datetime.datetime.now().isoformat(),
            "added_by": os.environ.get("USER", "unknown"),
            "sha256_hash": self.calculate_hash(),
            "processing_history": [],
        }
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the file"""
        sha256_hash = hashlib.sha256()
        with open(self.file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def log_processing_step(self, step_name: str, details: Dict = None):
        """Add processing step to the history"""
        if details is None:
            details = {}
        
        step = {
            "step": step_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "details": details
        }
        
        self.metadata["processing_history"].append(step)
        logger.info(f"Completed step: {step_name} for {self.original_filename}")
    
    def save_metadata(self):
        """Save metadata to YAML file"""
        metadata_file = METADATA_DIR / f"{self.original_filename}.metadata.yaml"
        with open(metadata_file, 'w') as f:
            yaml.dump(self.metadata, f, default_flow_style=False)
        logger.info(f"Metadata saved to {metadata_file}")
        
    def copy_to_raw_data(self):
        """Copy the original file to raw data directory with proper structure"""
        asset_type_dir = RAW_DATA_DIR / self._get_asset_type_dir()
        asset_type_dir.mkdir(exist_ok=True)
        
        # Create a destination path that includes the hash to ensure uniqueness
        hash_prefix = self.metadata["sha256_hash"][:8]
        dest_filename = f"{hash_prefix}_{self.original_filename}"
        destination = asset_type_dir / dest_filename
        
        # Copy the file
        shutil.copy2(self.file_path, destination)
        self.metadata["raw_data_path"] = str(destination)
        self.log_processing_step("raw_data_copy", {"destination": str(destination)})
        
        return destination
    
    def _get_asset_type_dir(self) -> str:
        """Return the directory name based on file type"""
        ext = self.file_extension
        if ext in ['.pdf']:
            return "documents"
        elif ext in ['.csv', '.xlsx', '.xls']:
            return "spreadsheets"
        elif ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
            return "images"
        elif ext in ['.mp4', '.mov', '.avi']:
            return "videos"
        elif ext in ['.osm', '.geojson', '.shp', '.kml']:
            return "gis"
        else:
            return "other"
    
    def process(self):
        """Main processing method to be implemented by subclasses"""
        # Implement in subclasses
        raise NotImplementedError("Subclasses must implement this method")


class PDFProcessor(AssetProcessor):
    """Processor for PDF documents"""
    
    def process(self):
        """Process PDF files"""
        # Copy to raw data
        raw_file_path = self.copy_to_raw_data()
        
        # Extract text content for searchability
        self.extract_text()
        
        # Extract metadata from PDF
        self.extract_pdf_metadata()
        
        # Save all metadata
        self.save_metadata()
        
        return self.metadata
    
    def extract_text(self):
        """Extract text content from PDF"""
        try:
            # This would be a placeholder for actual PDF text extraction
            # In a real implementation, use libraries like PyPDF2, pdfplumber, etc.
            self.metadata["has_text_extraction"] = True
            self.log_processing_step("text_extraction", {"status": "completed"})
        except Exception as e:
            logger.error(f"Error extracting text from PDF {self.original_filename}: {str(e)}")
            self.metadata["has_text_extraction"] = False
            self.log_processing_step("text_extraction", {"status": "failed", "error": str(e)})
    
    def extract_pdf_metadata(self):
        """Extract metadata from PDF document"""
        try:
            # This would be a placeholder for actual PDF metadata extraction
            # In a real implementation, use libraries like PyPDF2, pikepdf, etc.
            self.metadata["pdf_metadata"] = {
                "pages": 0,  # Replace with actual count
                "author": "Unknown",  # Replace with actual metadata
                "creation_date": "Unknown"  # Replace with actual metadata
            }
            self.log_processing_step("pdf_metadata_extraction", {"status": "completed"})
        except Exception as e:
            logger.error(f"Error extracting metadata from PDF {self.original_filename}: {str(e)}")
            self.log_processing_step("pdf_metadata_extraction", {"status": "failed", "error": str(e)})


class SpreadsheetProcessor(AssetProcessor):
    """Processor for CSV and Excel files"""
    
    def process(self):
        """Process spreadsheet files"""
        # Copy to raw data
        raw_file_path = self.copy_to_raw_data()
        
        # Extract basic stats
        self.extract_spreadsheet_stats()
        
        # Save all metadata
        self.save_metadata()
        
        return self.metadata
    
    def extract_spreadsheet_stats(self):
        """Extract basic statistics from spreadsheet"""
        try:
            # This would be a placeholder for actual spreadsheet analysis
            # In a real implementation, use libraries like pandas, openpyxl, etc.
            self.metadata["spreadsheet_stats"] = {
                "rows": 0,  # Replace with actual count
                "columns": 0,  # Replace with actual count
                "headers": []  # Replace with actual headers
            }
            self.log_processing_step("spreadsheet_stats_extraction", {"status": "completed"})
        except Exception as e:
            logger.error(f"Error analyzing spreadsheet {self.original_filename}: {str(e)}")
            self.log_processing_step("spreadsheet_stats_extraction", {"status": "failed", "error": str(e)})


class ImageProcessor(AssetProcessor):
    """Processor for image files"""
    
    def process(self):
        """Process image files"""
        # Copy to raw data
        raw_file_path = self.copy_to_raw_data()
        
        # Extract EXIF metadata
        self.extract_exif_metadata()
        
        # Save all metadata
        self.save_metadata()
        
        return self.metadata
    
    def extract_exif_metadata(self):
        """Extract EXIF metadata from images"""
        try:
            # This would be a placeholder for actual EXIF extraction
            # In a real implementation, use libraries like Pillow, exifread, etc.
            self.metadata["exif_data"] = {
                "datetime": "Unknown",  # Replace with actual EXIF date
                "gps_coordinates": None,  # Replace with actual GPS if available
                "camera_model": "Unknown"  # Replace with actual camera model
            }
            self.log_processing_step("exif_extraction", {"status": "completed"})
        except Exception as e:
            logger.error(f"Error extracting EXIF from image {self.original_filename}: {str(e)}")
            self.log_processing_step("exif_extraction", {"status": "failed", "error": str(e)})


class VideoProcessor(AssetProcessor):
    """Processor for video files"""
    
    def process(self):
        """Process video files"""
        # Copy to raw data
        raw_file_path = self.copy_to_raw_data()
        
        # Extract video metadata
        self.extract_video_metadata()
        
        # Generate thumbnail
        self.generate_thumbnail()
        
        # Create video log template
        self.create_video_log()
        
        # Save all metadata
        self.save_metadata()
        
        return self.metadata
    
    def extract_video_metadata(self):
        """Extract metadata from video file"""
        try:
            # This would be a placeholder for actual video metadata extraction
            # In a real implementation, use libraries like ffmpeg-python, moviepy, etc.
            self.metadata["video_metadata"] = {
                "duration": 0,  # Replace with actual duration
                "resolution": "Unknown",  # Replace with actual resolution
                "fps": 0,  # Replace with actual FPS
                "audio_tracks": 0  # Replace with actual count
            }
            self.log_processing_step("video_metadata_extraction", {"status": "completed"})
        except Exception as e:
            logger.error(f"Error extracting metadata from video {self.original_filename}: {str(e)}")
            self.log_processing_step("video_metadata_extraction", {"status": "failed", "error": str(e)})
    
    def generate_thumbnail(self):
        """Generate thumbnail from video"""
        try:
            # This would be a placeholder for actual thumbnail generation
            # In a real implementation, use libraries like ffmpeg-python, moviepy, etc.
            thumbnail_path = PROCESSED_DATA_DIR / "thumbnails" / f"{self.original_filename}.jpg"
            self.metadata["thumbnail_path"] = str(thumbnail_path)
            self.log_processing_step("thumbnail_generation", {"status": "completed", "path": str(thumbnail_path)})
        except Exception as e:
            logger.error(f"Error generating thumbnail for video {self.original_filename}: {str(e)}")
            self.log_processing_step("thumbnail_generation", {"status": "failed", "error": str(e)})
    
    def create_video_log(self):
        """Create a video log template for manual filling"""
        video_log_path = VIDEO_LOGS_DIR / f"{self.original_filename}.yml"
        
        try:
            log_template = {
                "video_id": "",  # To be filled manually or by YouTube processor
                "url": "",  # To be filled manually
                "title": self.original_filename,
                "channel_name": "",  # To be filled manually
                "channel_url": "",  # To be filled manually
                "upload_date": "",  # To be filled manually
                "retrieval_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "retrieved_by": os.environ.get("USER", "unknown"),
                "summary": "To be filled after watching or transcript analysis",
                "relevance_to_project": "To be filled manually",
                "downloaded_file_path": str(self.metadata.get("raw_data_path", "")),
                "file_sha256": self.metadata["sha256_hash"],
                "transcript_file_path": ""  # To be filled if transcript is downloaded
            }
            
            with open(video_log_path, 'w') as f:
                yaml.dump(log_template, f, default_flow_style=False)
            
            self.metadata["video_log_path"] = str(video_log_path)
            self.log_processing_step("video_log_creation", {"status": "completed", "path": str(video_log_path)})
        except Exception as e:
            logger.error(f"Error creating video log for {self.original_filename}: {str(e)}")
            self.log_processing_step("video_log_creation", {"status": "failed", "error": str(e)})


class YouTubeProcessor(AssetProcessor):
    """Processor for YouTube URLs"""
    
    def __init__(self, youtube_url: str):
        self.youtube_url = youtube_url
        self.video_id = self._extract_video_id(youtube_url)
        self.metadata = self._initialize_metadata()
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        # Very basic extraction - in production use a more robust method
        if "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        elif "youtube.com/watch" in url:
            import urllib.parse
            query = urllib.parse.urlparse(url).query
            params = urllib.parse.parse_qs(query)
            return params.get("v", [""])[0]
        return ""
    
    def _initialize_metadata(self) -> Dict:
        """Initialize metadata dictionary with YouTube-specific fields"""
        return {
            "youtube_url": self.youtube_url,
            "video_id": self.video_id,
            "date_added": datetime.datetime.now().isoformat(),
            "added_by": os.environ.get("USER", "unknown"),
            "processing_history": [],
        }
    
    def process(self):
        """Process YouTube URL"""
        # Download transcript if possible
        self.download_transcript()
        
        # Create video log template
        self.create_video_log()
        
        # Download video file (optional)
        # self.download_video()
        
        # Save all metadata
        self.save_metadata()
        
        return self.metadata
    
    def download_transcript(self):
        """Download transcript from YouTube video"""
        try:
            # In a real implementation, use yt-dlp
            transcript_command = f"yt-dlp --write-auto-sub --sub-lang en --skip-download \"{self.youtube_url}\""
            # In production code, use subprocess.run() to execute the command
            
            transcript_path = VIDEO_LOGS_DIR / f"{self.video_id}.en.vtt"
            self.metadata["transcript_path"] = str(transcript_path)
            self.log_processing_step("transcript_download", {
                "status": "completed", 
                "path": str(transcript_path),
                "command": transcript_command
            })
        except Exception as e:
            logger.error(f"Error downloading transcript for {self.youtube_url}: {str(e)}")
            self.log_processing_step("transcript_download", {"status": "failed", "error": str(e)})
    
    def create_video_log(self):
        """Create a video log template for manual filling"""
        video_log_path = VIDEO_LOGS_DIR / f"{self.video_id}.yml"
        
        try:
            log_template = {
                "video_id": self.video_id,
                "url": self.youtube_url,
                "title": "",  # To be filled manually or via YouTube API
                "channel_name": "",  # To be filled manually or via YouTube API
                "channel_url": "",  # To be filled manually or via YouTube API
                "upload_date": "",  # To be filled manually or via YouTube API
                "retrieval_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "retrieved_by": os.environ.get("USER", "unknown"),
                "summary": "To be filled after watching or transcript analysis",
                "relevance_to_project": "To be filled manually",
                "downloaded_file_path": "",  # To be filled if video is downloaded
                "transcript_file_path": self.metadata.get("transcript_path", "")
            }
            
            with open(video_log_path, 'w') as f:
                yaml.dump(log_template, f, default_flow_style=False)
            
            self.metadata["video_log_path"] = str(video_log_path)
            self.log_processing_step("video_log_creation", {"status": "completed", "path": str(video_log_path)})
        except Exception as e:
            logger.error(f"Error creating video log for {self.youtube_url}: {str(e)}")
            self.log_processing_step("video_log_creation", {"status": "failed", "error": str(e)})
    
    def save_metadata(self):
        """Save metadata to YAML file"""
        metadata_file = METADATA_DIR / f"youtube_{self.video_id}.metadata.yaml"
        with open(metadata_file, 'w') as f:
            yaml.dump(self.metadata, f, default_flow_style=False)
        logger.info(f"Metadata saved to {metadata_file}")


class GISDataProcessor(AssetProcessor):
    """Processor for GIS data files (OSM, GeoJSON, Shapefiles, KML)"""
    
    def process(self):
        """Process GIS data files"""
        # Copy to raw data
        raw_file_path = self.copy_to_raw_data()
        
        # Extract GIS metadata
        self.extract_gis_metadata()
        
        # Save all metadata
        self.save_metadata()
        
        return self.metadata
    
    def extract_gis_metadata(self):
        """Extract metadata from GIS file"""
        try:
            # This would be a placeholder for actual GIS metadata extraction
            # In a real implementation, use libraries like geopandas, pyshp, etc.
            self.metadata["gis_metadata"] = {
                "file_type": self.file_extension,
                "feature_count": 0,  # Replace with actual count
                "bbox": [0, 0, 0, 0],  # Replace with actual bounding box
                "crs": "Unknown"  # Replace with actual CRS
            }
            self.log_processing_step("gis_metadata_extraction", {"status": "completed"})
        except Exception as e:
            logger.error(f"Error extracting metadata from GIS file {self.original_filename}: {str(e)}")
            self.log_processing_step("gis_metadata_extraction", {"status": "failed", "error": str(e)})


def get_processor_for_file(file_path: Union[str, Path]) -> AssetProcessor:
    """Factory function to get the appropriate processor for a file based on extension"""
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    
    if extension == '.pdf':
        return PDFProcessor(file_path)
    elif extension in ['.csv', '.xlsx', '.xls']:
        return SpreadsheetProcessor(file_path)
    elif extension in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
        return ImageProcessor(file_path)
    elif extension in ['.mp4', '.mov', '.avi']:
        return VideoProcessor(file_path)
    elif extension in ['.osm', '.geojson', '.shp', '.kml']:
        return GISDataProcessor(file_path)
    else:
        # Default to base processor for unknown types
        return AssetProcessor(file_path)


def is_youtube_url(url: str) -> bool:
    """Check if a string is a YouTube URL"""
    return url.startswith(('https://www.youtube.com/', 
                          'https://youtube.com/', 
                          'https://youtu.be/'))


def process_file(file_path_or_url: str) -> Dict:
    """Process a file or URL and return its metadata"""
    if is_youtube_url(file_path_or_url):
        processor = YouTubeProcessor(file_path_or_url)
    else:
        processor = get_processor_for_file(file_path_or_url)
    
    return processor.process()


def process_directory(directory_path: str, recursive: bool = False) -> List[Dict]:
    """Process all files in a directory"""
    directory_path = Path(directory_path)
    processed_files = []
    
    # Get list of files
    if recursive:
        files = [f for f in directory_path.glob('**/*') if f.is_file()]
    else:
        files = [f for f in directory_path.glob('*') if f.is_file()]
    
    # Process each file
    for file_path in files:
        try:
            metadata = process_file(str(file_path))
            processed_files.append(metadata)
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
    
    return processed_files


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description='Process files for Mariupol documentation project')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', help='Path to a file to process')
    group.add_argument('-d', '--directory', help='Path to a directory of files to process')
    group.add_argument('-y', '--youtube', help='YouTube URL to process')
    
    parser.add_argument('-r', '--recursive', action='store_true', 
                        help='Process directories recursively')
    
    args = parser.parse_args()
    
    try:
        if args.file:
            metadata = process_file(args.file)
            print(f"Processed file: {args.file}")
            
        elif args.directory:
            processed_files = process_directory(args.directory, args.recursive)
            print(f"Processed {len(processed_files)} files from {args.directory}")
            
        elif args.youtube:
            metadata = process_file(args.youtube)
            print(f"Processed YouTube URL: {args.youtube}")
            
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
