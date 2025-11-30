import json
import base64
import subprocess
import os

def handler(event, context):
    """Handles the request by extracting the direct download URL via yt-dlp."""
    try:
        encoded_url = event['queryStringParameters'].get('ytlink')
        
        if not encoded_url:
            return { 'statusCode': 400, 'body': json.dumps({'error': 'Missing YouTube link parameter.'}) }

        # Decode the link received from the Telegram bot/index.html
        youtube_url = base64.b64decode(encoded_url).decode('utf-8')

        # Use yt-dlp to get the best quality *single file* MP4 format
        # This is crucial to avoid FFmpeg dependency on Netlify
        command = [
            'yt-dlp',
            '--no-warnings',
            '-f', 'best[ext=mp4]/best', 
            '--dump-json',
            youtube_url
        ]
        
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        video_info = json.loads(process.stdout)
        
        download_url = video_info.get('url') 
        
        if not download_url:
             return { 'statusCode': 500, 'body': json.dumps({'error': 'Could not extract download URL.'}) }

        # Redirect the user to the direct download link
        return {
            'statusCode': 302, 
            'headers': {
                'Location': download_url,
                'Cache-Control': 'no-cache'
            },
            'body': ''
        }

    except subprocess.CalledProcessError as e:
        # Handle errors like private video, geo-blocked, etc.
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Video processing failed. Try another link.'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'An unexpected error occurred.'})
        }