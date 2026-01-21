
import asyncio
import base64
import os
import sys
import logging

# Add project root to path
sys.path.insert(0, os.getcwd())

# Import registry to verify bridge integration
from core.bridge.registry import TOOL_REGISTRY
from tools.deepfake_scanner import scan_media

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_e2e_simulation():
    print("🚀 Starting End-to-End Simulation: Deepfake Scanner")
    
    # 1. Verify Registration in HTTP Bridge Registry
    print("   Verifying tool registration in 'core.bridge.registry'...")
    if "deepfake_scan_tool" in TOOL_REGISTRY:
        print("   ✅ 'deepfake_scan_tool' is successfully REGISTERED in HTTP Bridge.")
    else:
        print(f"   ❌ FATAL: Tool not found in Bridge Registry. Available: {list(TOOL_REGISTRY.keys())}")
        return

    # 2. Prepare Payload (Frontend -> Backend)
    # We'll use a small in-memory dummy video bytes
    video_path = "tests/test_video.mp4"
    if not os.path.exists(video_path):
        # Regenerate dummy video if missing
        print("   Generating dummy video artifact...")
        os.system('ffmpeg -f lavfi -i testsrc=duration=1:size=1280x720:rate=30 -metadata encoder="Lavf Fake Encoder" -y tests/test_video.mp4 > /dev/null 2>&1')

    with open("tests/test_video.mp4", "rb") as f:
        file_bytes = f.read()
        file_b64 = base64.b64encode(file_bytes).decode('utf-8')

    print(f"   Payload prepared: {len(file_b64)} chars base64")

    # 3. Execute Tool Logic (Backend Logic)
    print("⚡ Simulating Tool Execution (scan_media)...")
    try:
        # Calling the logic function directly (simulating the wrapper call)
        result = await scan_media(
            file_b64=file_b64,
            mime_type="video/mp4",
            filename="simulation_video.mp4"
        )
        
        # 4. Validate Response (Backend -> Frontend)
        print("\n✅ RESPONSE RECEIVED")
        print(f"   Is Deepfake: {result['is_deepfake']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Source: {result['source']}")
        
        details = result['details']
        if 'metadata' in details:
            print(f"   Metadata Extracted: {list(details['metadata'].keys())}")
            if 'encoder' in details['metadata']:
                print(f"   Encoder Found: {details['metadata']['encoder']}")
        
        if 'flags' in details: # Check legacy 'flags' or new 'metadata_flags'
             print(f"   Flags: {details.get('flags')}")
        
        if 'metadata_flags' in details:
             print(f"   Metadata Flags: {details.get('metadata_flags')}")

        if result['source'] == "Gemini 3 Forensics" or result['source'] == "FFprobe Metadata":
             print("\n🎉 SUCCESS: The pipeline is fully integrated.")
        else:
             print(f"\n⚠️ WARNING: Source was {result['source']}, check logic.")

    except Exception as e:
        print(f"\n❌ FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_e2e_simulation())
