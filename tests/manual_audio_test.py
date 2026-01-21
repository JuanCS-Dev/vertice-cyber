
import asyncio
import base64
import os
import sys
import logging

# Add project root to path
sys.path.insert(0, os.getcwd())

from tools.deepfake_scanner import scan_media

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_test():
    audio_path = "tests/test_audio.mp3"
    
    if not os.path.exists(audio_path):
        print(f"❌ Error: File {audio_path} not found.")
        return

    print(f"🔍 Scanning {audio_path} for metadata...")
    
    try:
        with open(audio_path, "rb") as f:
            file_bytes = f.read()
            file_b64 = base64.b64encode(file_bytes).decode('utf-8')
            
        result = await scan_media(file_b64, "audio/mpeg", "test_audio.mp3")
        
        print("\n📊 --- SCAN RESULT ---")
        print(f"Source: {result['source']}")
        
        details = result['details']
        if 'error' in details:
             print(f"❌ Error: {details['error']}")

        if 'metadata' in details:
            print("\n📂 Metadata Found:")
            for k, v in details['metadata'].items():
                print(f"  - {k}: {v}")
        
        if 'metadata_flags' in details:
            print("\n🚩 Flags:")
            for flag in details['metadata_flags']:
                print(f"  - {flag}")

        print("----------------------\n")
        
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_test())
