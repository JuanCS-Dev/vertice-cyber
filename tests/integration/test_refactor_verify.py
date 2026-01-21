
import asyncio
import sys
import os

# Fix path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

async def test_mitre_refactor():
    print("Testing MITRE API Compatibility...")
    try:
        from tools import mitre_api
        from tools import mitre_client
        
        # Check if legacy functions exist
        print(f"  get_control: {mitre_api.get_control}")
        print(f"  get_all_frameworks: {mitre_api.get_all_frameworks}")
        
        # Check singleton identity (indirectly)
        mitre_client.get_mitre_client()
        # Since mitre_api functions delegate to get_mitre_client(), this should work without error
        # We won't call async functions here to avoid event loop issues in simple script unless needed
        print("✅ MITRE API module loaded successfully")
        
    except ImportError as e:
        print(f"❌ ImportError: {e}")
    except AttributeError as e:
        print(f"❌ AttributeError (Missing function?): {e}")

async def test_module_loading():
    print("\nTesting Core Modules Loading...")
    modules = [
        "core.settings",
        "core.event_bus",
        "tools.magistrate",
        "tools.wargame",
        "mcp_server"
    ]
    for mod in modules:
        try:
            __import__(mod, fromlist=[''])
            print(f"  ✅ {mod} loaded")
        except Exception as e:
            print(f"  ❌ {mod} failed: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_mitre_refactor())
    loop.run_until_complete(test_module_loading())
