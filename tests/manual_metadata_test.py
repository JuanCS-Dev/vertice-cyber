
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
    image_path = "docs/assets/images/banner_v2.4.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ Error: File {image_path} not found.")
        return

    print(f"🔍 Scanning {image_path} for metadata...")
    
    try:
        with open(image_path, "rb") as f:
            file_bytes = f.read()
            file_b64 = base64.b64encode(file_bytes).decode('utf-8')
            
        result = await scan_media(file_b64, "image/jpeg", "banner_v2.4.jpg")
        
        print("\n📊 --- SCAN RESULT ---")
        print(f"Is Deepfake: {result['is_deepfake']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Source: {result['source']}")
        
        details = result['details']
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
