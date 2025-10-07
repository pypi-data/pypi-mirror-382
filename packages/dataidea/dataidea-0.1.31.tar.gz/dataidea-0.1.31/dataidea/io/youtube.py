"""
Functions for downloading YouTube videos
"""
import os
import re
import logging
import yt_dlp

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_url(url):
    """
    Check if the provided URL is a valid YouTube URL.
    
    Parameters:
    -----------
    url : str
        The URL to check
        
    Returns:
    --------
    bool
        True if the URL is a valid YouTube URL, False otherwise
    """
    if not url:
        return False
    youtube_regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$'
    return re.match(youtube_regex, url) is not None

def download(url=None, output_folder=''):
    """
    Downloads a YouTube video.
    
    Parameters:
    -----------
    url : str
        YouTube video URL
    output_folder : str, default=''
        Directory to save the downloaded video
        
    Returns:
    --------
    bool
        True if the download was successful, False otherwise
    """
    if not url or not is_valid_url(url):
        logger.error("Invalid URL provided.")
        return False

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logger.info(f"Output folder '{output_folder}' created.")

    options = {
        'format': 'best',
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'quiet': False,
        'no_warnings': False,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            logger.info("Downloading video...")
            ydl.download([url])
            logger.info("Download completed successfully!")
            return True
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Download error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    
    return False

__all__ = ['download', 'is_valid_url'] 