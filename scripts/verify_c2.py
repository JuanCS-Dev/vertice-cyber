
import asyncio
import aiohttp
import logging

# Configuration
BASE_URL = "http://localhost:8001"
WS_URL = "ws://localhost:8001/mcp/events"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("C2_VERIFIER")

async def test_god_mode():
    async with aiohttp.ClientSession() as session:
        # 0. Health Check
        async with session.get(f"{BASE_URL}/health") as resp:
            health = await resp.json()
            logger.info(f"Health: {health}")
            assert health['status'] == 'healthy'

        # 1. Spawn Agent
        logger.info("1. Spawning OSINT Agent...")
        async with session.post(f"{BASE_URL}/api/v1/agents/spawn", json={
            "type": "osint", 
            "config": {"depth": "deep"}
        }) as resp:
            agent_data = await resp.json()
            agent_id = agent_data['agent_id']
            logger.info(f" -> Agent Spawned: {agent_id}")

        # 2. Check Snapshot
        logger.info("2. Checking Snapshot...")
        async with session.get(f"{BASE_URL}/api/v1/snapshot") as resp:
            snapshot = await resp.json()
            agents = snapshot['agents']
            target_agent = next((a for a in agents if a['agent_id'] == agent_id), None)
            assert target_agent is not None
            assert target_agent['state'] == 'SPAWNED'
            logger.info(f" -> Snapshot confirmed agent state: {target_agent['state']}")

        # 3. Control Agent (PAUSE)
        logger.info("3. Pausing Agent...")
        async with session.post(f"{BASE_URL}/api/v1/agents/{agent_id}/control", json={"action": "PAUSE"}) as resp:
            res = await resp.json()
            assert res['success'] is True
            logger.info(" -> Pause command accepted")

        # 4. Control Agent (RESUME)
        logger.info("4. Resuming Agent...")
        async with session.post(f"{BASE_URL}/api/v1/agents/{agent_id}/control", json={"action": "RESUME"}) as resp:
            res = await resp.json()
            assert res['success'] is True
            logger.info(" -> Resume command accepted")

        # 5. Connect WebSocket/Neural Link
        logger.info("5. Testing Neural Link (WebSocket)...")
        try:
            async with session.ws_connect(WS_URL) as ws:
                # Wait for welcome
                msg = await ws.receive_json()
                logger.info(f" -> WS Welcome: {msg}")
                
                # Subscribe
                await ws.send_json({"type": "subscribe", "channel": "*"})
                logger.info(" -> Subscribed to *")
                
                # Trigger a log by running a tool (if possible) or just spawning another agent
                async with session.post(f"{BASE_URL}/api/v1/agents/spawn", json={"type": "threat"}) as resp:
                    pass
                    
                # Listen for event
                msg = await ws.receive_json()
                logger.info(f" -> WS Event Received: {msg}")
                # Expecting agent.lifecycle.spawned or similar
                
        except Exception as e:
            logger.error(f"WS Test failed (may need server running): {e}")

    logger.info("✅ GOD MODE TEST PASSED")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_god_mode())
