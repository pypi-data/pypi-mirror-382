#!/usr/bin/env python3
"""
Basic test to verify scaledown-new package functionality
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_imports():
    """Test basic imports work"""
    print("Testing basic imports...")

    try:
        # Test main package import
        import scaledown
        print("✅ Main scaledown package imported")

        # Test ScaleDown class
        from scaledown import ScaleDown
        print("✅ ScaleDown class imported")

        # Test tools
        from scaledown.tools import tools
        print("✅ tools function imported")

        # Test optimization functions
        from scaledown import optimize_prompt, parse_optimizers
        print("✅ Optimization functions imported")

        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_optimization_pipeline():
    """Test the optimization pipeline"""
    print("\nTesting optimization pipeline...")

    try:
        from scaledown import optimize_prompt, parse_optimizers

        # Test parser
        optimizers = parse_optimizers('expert_persona,cot')
        print(f"✅ Parsed optimizers: {optimizers}")

        # Test optimization
        question = "What is machine learning?"
        optimized = optimize_prompt(question, optimizers)
        print(f"✅ Optimization successful: {len(optimized)} chars")

        return True
    except Exception as e:
        print(f"❌ Optimization error: {e}")
        return False

def test_scaledown_class():
    """Test ScaleDown class functionality"""
    print("\nTesting ScaleDown class...")

    try:
        from scaledown import ScaleDown

        # Initialize
        sd = ScaleDown()
        print("✅ ScaleDown initialized")

        # Test methods
        optimizers = sd.list_optimizers()
        print(f"✅ Listed {len(optimizers)} optimizers")

        styles = sd.get_optimization_styles()
        print(f"✅ Listed {len(styles)} optimization styles")

        # Test optimization
        report = sd.optimize_with_pipeline("Test question", ['cot'])
        print(f"✅ Pipeline optimization: {report['optimization_count']} optimizers")

        return True
    except Exception as e:
        print(f"❌ ScaleDown error: {e}")
        return False

def test_tools_api():
    """Test tools API backward compatibility"""
    print("\nTesting tools API...")

    try:
        from scaledown.tools import tools

        # Test legacy API
        result = tools(optimiser='cot')
        print(f"✅ Legacy tools API: {list(result.keys())}")

        # Test enhanced API
        result = tools(optimiser='expert_persona,cot', enable_enhanced_features=True)
        print(f"✅ Enhanced tools API: {list(result.keys())}")

        return True
    except Exception as e:
        print(f"❌ Tools API error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing ScaleDown v0.2.0 Package")
    print("=" * 40)

    tests = [
        test_basic_imports,
        test_optimization_pipeline,
        test_scaledown_class,
        test_tools_api
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 40)
    print(f"Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All tests passed! ScaleDown v0.2.0 is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)