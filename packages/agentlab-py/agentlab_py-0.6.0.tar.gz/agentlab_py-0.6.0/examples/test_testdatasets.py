#!/usr/bin/env python3
"""Simple test script to verify test datasets SDK functions work correctly."""

import os
import sys
from agentlab import AgentLabClient, AgentLabClientOptions


def test_list_test_datasets():
    """Test listing test datasets."""
    print("Testing list_test_datasets()...")
    
    client = AgentLabClient(AgentLabClientOptions())
    
    try:
        response = client.list_test_datasets()
        print(f"✅ list_test_datasets() works!")
        print(f"   Found {len(response.test_datasets)} dataset(s)")
        
        if response.test_datasets:
            print(f"   First dataset: {response.test_datasets[0].name}")
        
        return True
    except Exception as e:
        print(f"❌ list_test_datasets() failed: {e}")
        return False


def test_get_tests_with_invalid_id():
    """Test get_tests with an invalid ID to verify error handling."""
    print("\nTesting get_tests() error handling with invalid ID...")
    
    client = AgentLabClient(AgentLabClientOptions())
    
    try:
        # This should fail gracefully
        response = client.get_tests("invalid-id")
        print(f"❌ Should have failed but got: {response}")
        return False
    except Exception as e:
        print(f"✅ get_tests() correctly handles errors")
        print(f"   Error message: {str(e)[:100]}...")
        return True


def test_response_models():
    """Test that response models have correct structure."""
    print("\nTesting response model structure...")
    
    client = AgentLabClient(AgentLabClientOptions())
    
    try:
        response = client.list_test_datasets()
        
        # Check response has required attributes
        assert hasattr(response, 'test_datasets'), "Response missing 'test_datasets'"
        assert hasattr(response, 'next_page_token'), "Response missing 'next_page_token'"
        
        # Check response has methods
        assert hasattr(response, 'to_dict'), "Response missing 'to_dict' method"
        assert hasattr(response, 'to_json'), "Response missing 'to_json' method"
        
        # Try calling the methods
        response_dict = response.to_dict()
        response_json = response.to_json()
        
        assert isinstance(response_dict, dict), "to_dict() should return dict"
        assert isinstance(response_json, str), "to_json() should return str"
        
        print("✅ Response models have correct structure")
        print(f"   - test_datasets: {len(response.test_datasets)} items")
        print(f"   - next_page_token: {repr(response.next_page_token)}")
        print(f"   - to_dict() returns: {type(response_dict).__name__}")
        print(f"   - to_json() returns: {type(response_json).__name__}")
        
        return True
    except Exception as e:
        print(f"❌ Response model structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Test Datasets SDK Functions Test Suite")
    print("=" * 60)
    
    # Check API token
    if not os.getenv("AGENTLAB_API_TOKEN"):
        print("⚠️  Error: AGENTLAB_API_TOKEN environment variable is not set.")
        print("Please set it before running tests:")
        print("  export AGENTLAB_API_TOKEN=your_api_token_here")
        sys.exit(1)
    
    print()
    
    # Run tests
    results = []
    results.append(("list_test_datasets", test_list_test_datasets()))
    results.append(("get_tests error handling", test_get_tests_with_invalid_id()))
    results.append(("response models", test_response_models()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

