# tests/test_complete.py
import sys
import os
import secrets
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from TBuddy_SDK import RingmasterClient, RingmasterConfig
from TBuddy_SDK.models import StreamUpdate


class TestSuite:
    """Complete test suite for SDK"""

    def __init__(self):
        # Generate a valid dummy API key (>= 10 characters)
        dummy_api_key = secrets.token_hex(8)  # 16-character hex string
        
        self.config = RingmasterConfig(
            api_key=dummy_api_key,
            base_url="http://localhost:8000",
            log_level="INFO"
        )
        self.session_id = None

    async def test_1_new_query(self):
        """Test 1: Submit new query"""
        print("\n🧪 Test 1: New Query")
        print("-" * 50)

        async with RingmasterClient(self.config) as client:
            result = await client.submit_query(
                "Plan a 3-day trip to Paris from London on dates 11th, 12th, 13th October with budget under 30000k",
                wait_for_completion=True
            )

            assert result.session_id is not None
            assert result.status == "completed"
            assert result.destination is not None

            self.session_id = result.session_id

            print(f"✅ Session ID: {result.session_id}")
            print(f"✅ Destination: {result.destination}")
            print(f"✅ Status: {result.status}")

    async def test_2_follow_up(self):
        """Test 2: Follow-up query"""
        print("\n🧪 Test 2: Follow-up Query")
        print("-" * 50)

        async with RingmasterClient(self.config) as client:
            result = await client.submit_query(
                "Change budget to $2000",
                session_id=self.session_id,
                wait_for_completion=True
            )

            assert result.is_follow_up is True
            assert result.session_id == self.session_id

            print(f"✅ Is Follow-up: {result.is_follow_up}")
            print(f"✅ Update Type: {result.update_type}")

    async def test_3_session_memory(self):
        """Test 3: Get session memory"""
        print("\n🧪 Test 3: Session Memory")
        print("-" * 50)

        async with RingmasterClient(self.config) as client:
            memory = await client.get_session_memory(self.session_id)

            assert memory.exists is True
            assert memory.destination is not None

            print(f"✅ Memory exists: {memory.exists}")
            print(f"✅ Destination: {memory.destination}")
            print(f"✅ Conversation turns: {memory.conversation_turns}")

    async def test_4_websocket(self):
        """Test 4: WebSocket streaming"""
        print("\n🧪 Test 4: WebSocket Streaming")
        print("-" * 50)

        updates_received = []

        async def on_update(update: StreamUpdate):
            updates_received.append(update)
            print(f"📡 {update.agent}: {update.message} ({update.progress_percent}%)")

        async with RingmasterClient(self.config) as client:
            result = await client.submit_query(
                "Plan a trip to Tokyo",
                stream_callback=on_update,
                wait_for_completion=True
            )

            assert len(updates_received) > 0
            print(f"✅ Received {len(updates_received)} updates")

    async def test_5_health_check(self):
        """Test 5: Health check"""
        print("\n🧪 Test 5: Health Check")
        print("-" * 50)

        async with RingmasterClient(self.config) as client:
            health = await client.health_check()

            print(f"✅ Status: {health.status}")
            print(f"✅ Orchestrator: {health.orchestrator}")

    async def run_all(self):
        """Run all tests"""
        print("=" * 50)
        print("🚀 Ringmaster SDK Test Suite")
        print("=" * 50)

        try:
            await self.test_1_new_query()
            await self.test_2_follow_up()
            await self.test_3_session_memory()
            # await self.test_4_websocket() 
            await self.test_5_health_check()

            print("\n" + "=" * 50)
            print("✅ All tests passed!")
            print("=" * 50)

        except AssertionError as e:
            print(f"\n❌ Assertion failed: {e}")
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()


async def main():
    suite = TestSuite()
    await suite.run_all()


if __name__ == "__main__":
    asyncio.run(main())
