#!/usr/bin/env python3
"""
Test all fixed features across all serializers.
"""

import sys
from pathlib import Path
from decimal import Decimal
from dataclasses import dataclass
from typing import List, Dict, Any, Union

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "xwsystem" / "src"))

def test_fixed_features():
    """Test all fixed features across all serializers."""
    print("🧪 Testing Fixed Features Across All Serializers")
    print("=" * 60)
    print()
    
    try:
        from exonware.xsystem.serialization.json import JsonSerializer
        from exonware.xsystem.serialization.xml import XmlSerializer
        from exonware.xsystem.serialization.toml import TomlSerializer
        from exonware.xsystem.serialization.yaml import YamlSerializer
        from exonware.xsystem.serialization.contracts import SerializationFormat
        
        # Test data
        test_data = {
            "users": [
                {"id": 1, "name": "Alice", "age": 30, "active": True},
                {"id": 2, "name": "Bob", "age": 25, "active": False}
            ],
            "metadata": {
                "version": "1.0",
                "created": "2025-01-01T00:00:00Z"
            }
        }
        
        # Test dataclass for typed decoding
        @dataclass
        class User:
            id: int
            name: str
            age: int
            active: bool
        
        # Initialize serializers
        serializers = {
            "JSON": JsonSerializer(),
            "XML": XmlSerializer(),
            "TOML": TomlSerializer(),
            "YAML": YamlSerializer()
        }
        
        # Test results
        results = {}
        
        for format_name, serializer in serializers.items():
            print(f"🔧 Testing {format_name} Fixed Features")
            print("-" * 40)
            
            format_results = {}
            
            # Test basic serialization
            try:
                text_data = serializer.dumps_text(test_data)
                parsed_data = serializer.loads_text(text_data)
                format_results["Basic Serialization"] = "✅ Working"
                print(f"✅ Basic Serialization: {len(text_data)} chars")
            except Exception as e:
                format_results["Basic Serialization"] = f"❌ Failed: {str(e)[:50]}..."
                print(f"❌ Basic Serialization: {e}")
            
            # Test format detection
            try:
                detected_format = serializer.sniff_format(text_data)
                format_results["Format Detection"] = "✅ Working"
                print(f"✅ Format Detection: {detected_format}")
            except Exception as e:
                format_results["Format Detection"] = f"❌ Failed: {str(e)[:50]}..."
                print(f"❌ Format Detection: {e}")
            
            # Test partial access
            try:
                name = serializer.get_at(text_data, "users.0.name")
                updated_data = serializer.set_at(text_data, "users.0.name", "Alice Updated")
                path_values = list(serializer.iter_path(text_data, "users.0"))
                format_results["Partial Access"] = "✅ Working"
                print(f"✅ Partial Access: get='{name}', set={len(updated_data)} chars, iter={len(path_values)} items")
            except Exception as e:
                format_results["Partial Access"] = f"❌ Failed: {str(e)[:50]}..."
                print(f"❌ Partial Access: {e}")
            
            # Test patching
            try:
                patch = [{"op": "replace", "path": "users.0.name", "value": "Alice Patched"}]
                patched_data = serializer.apply_patch(text_data, patch)
                format_results["Patching"] = "✅ Working"
                print(f"✅ Patching: {len(patched_data)} chars")
            except Exception as e:
                format_results["Patching"] = f"❌ Failed: {str(e)[:50]}..."
                print(f"❌ Patching: {e}")
            
            # Test schema validation
            try:
                schema = {"users": list, "metadata": dict}
                is_valid = serializer.validate_schema(text_data, schema)
                format_results["Schema Validation"] = "✅ Working"
                print(f"✅ Schema Validation: {is_valid}")
            except Exception as e:
                format_results["Schema Validation"] = f"❌ Failed: {str(e)[:50]}..."
                print(f"❌ Schema Validation: {e}")
            
            # Test canonical serialization
            try:
                canonical = serializer.canonicalize(test_data)
                hash_stable = serializer.hash_stable(test_data)
                format_results["Canonical Serialization"] = "✅ Working"
                print(f"✅ Canonical: {len(canonical)} chars, hash={hash_stable[:16]}...")
            except Exception as e:
                format_results["Canonical Serialization"] = f"❌ Failed: {str(e)[:50]}..."
                print(f"❌ Canonical Serialization: {e}")
            
            # Test batch streaming
            try:
                rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
                batch_chunks = list(serializer.serialize_ndjson(rows))
                batch_deserialized = list(serializer.deserialize_ndjson(batch_chunks))
                format_results["Batch Streaming"] = "✅ Working"
                print(f"✅ Batch Streaming: {len(batch_chunks)} chunks, {len(batch_deserialized)} items")
            except Exception as e:
                format_results["Batch Streaming"] = f"❌ Failed: {str(e)[:50]}..."
                print(f"❌ Batch Streaming: {e}")
            
            results[format_name] = format_results
            print()
        
        # Summary table
        print("=" * 60)
        print("📊 FIXED FEATURES SUMMARY")
        print("=" * 60)
        
        # Print header
        print(f"{'Feature':<25} {'JSON':<8} {'XML':<8} {'TOML':<8} {'YAML':<8}")
        print("-" * 60)
        
        # Print each feature status
        features = [
            "Basic Serialization", "Format Detection", "Partial Access", 
            "Patching", "Schema Validation", "Canonical Serialization", "Batch Streaming"
        ]
        
        for feature_name in features:
            json_status = "✅" if "Working" in results["JSON"].get(feature_name, "") else "❌"
            xml_status = "✅" if "Working" in results["XML"].get(feature_name, "") else "❌"
            toml_status = "✅" if "Working" in results["TOML"].get(feature_name, "") else "❌"
            yaml_status = "✅" if "Working" in results["YAML"].get(feature_name, "") else "❌"
            
            print(f"{feature_name:<25} {json_status:<8} {xml_status:<8} {toml_status:<8} {yaml_status:<8}")
        
        print("\n🎉 Fixed features testing completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_features()
    sys.exit(0 if success else 1)
