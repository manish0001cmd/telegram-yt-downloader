import json
import base64
import subprocess
import os

def handler(event, context):
    """
    Handles the request to get the YouTube video download link.
    """
    try:
        # 1. Get the encoded YouTube link from the URL parameters
        encoded_url = event['queryStringParameters'].get('ytlink')
        
        if not encoded_url:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing YouTube link parameter.'})
            }

        # 2. Decode the URL (The bot will base64 encode it for safety)
        youtube_url = base64.b64decode(encoded_url).decode('utf-8')

        # 3. Use yt-dlp to extract video info (High Quality)
        # Configure yt-dlp to get the best quality MP4 video stream
        command = [
            'yt-dlp',
            '--no-warnings',
            # Prioritize high-quality MP4 formats
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 
            '--dump-json',
            youtube_url
        ]
        
        # Run the command and capture output
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        video_info = json.loads(process.stdout)
        
        # 4. Get the direct download URL from the extracted info
        download_url = video_info.get('url') 
        
        if not download_url:
             return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Could not extract download URL.'})
            }

        # 5. Redirect the user to the direct download link
        # 302 (Found) is the standard code for temporary redirect
        return {
            'statusCode': 302, 
            'headers': {
                'Location': download_url,
                'Cache-Control': 'no-cache'
            },
            'body': ''
        }

    except subprocess.CalledProcessError as e:
        # Handle yt-dlp errors (e.g., video not available, private video)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Video processing error: {e.stderr.strip()}'})
        }
    except Exception as e:
        # Handle general errors
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'An unexpected error occurred: {str(e)}'})
        }