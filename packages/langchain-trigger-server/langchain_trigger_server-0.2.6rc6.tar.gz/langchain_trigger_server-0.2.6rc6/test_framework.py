"""Test script to verify the triggers framework."""

import asyncio
import json
from typing import Dict, Any

import httpx


async def test_email_trigger():
    """Test the email trigger endpoint."""
    print("🧪 Testing email trigger...")
    
    payload = {
        "from": "sam@example.com",
        "to": "support@company.com", 
        "subject": "Test Email",
        "body": "This is a test email from the triggers framework."
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/triggers/email",
                json=payload,
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Email trigger success: {result}")
                return True
            else:
                print(f"❌ Email trigger failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Email trigger error: {e}")
            return False


async def test_slack_trigger():
    """Test the Slack trigger endpoint."""
    print("🧪 Testing Slack trigger...")
    
    payload = {
        "event": {
            "user": "U1234567",
            "channel": "C1234567",
            "text": "Hello from the triggers framework!",
            "ts": "1234567890.123456"
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/triggers/slack",
                json=payload,
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Slack trigger success: {result}")
                return True
            else:
                print(f"❌ Slack trigger failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Slack trigger error: {e}")
            return False


async def test_api_endpoints():
    """Test the built-in API endpoints."""
    print("🧪 Testing API endpoints...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test root endpoint
            response = await client.get("http://localhost:8000/")
            if response.status_code == 200:
                print(f"✅ Root endpoint: {response.json()}")
            
            # Test health endpoint
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print(f"✅ Health endpoint: {response.json()}")
            
            # Test triggers list
            response = await client.get("http://localhost:8000/triggers")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Triggers list: Found {result['count']} triggers")
                for trigger in result['triggers']:
                    print(f"   - {trigger['name']}: {trigger['event_type']}")
            
            # Test event subscriptions
            response = await client.get("http://localhost:8000/events/subscriptions")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Event subscriptions: {result}")
            
            return True
            
        except Exception as e:
            print(f"❌ API endpoints error: {e}")
            return False


async def run_all_tests():
    """Run all tests."""
    print("🚀 Starting triggers framework tests...")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    await asyncio.sleep(2)
    
    tests = [
        test_api_endpoints,
        test_email_trigger,
        test_slack_trigger,
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            results.append(False)
        
        print()  # Add spacing between tests
    
    # Summary
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the server logs.")


if __name__ == "__main__":
    print("Please start the server with: python example_server.py")
    print("Then run this test script in another terminal.")
    print()
    
    asyncio.run(run_all_tests())