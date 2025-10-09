"""
Test Script 2: Probe Discovery
Tests listing and filtering probes with different parameters
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modelred import ModelRed

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")


def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_probe_discovery():
    """Test listing and filtering probes"""

    print_section("TEST 2: PROBE DISCOVERY")

    # Initialize client
    api_key = os.getenv("MODELRED_API_KEY")
    if not api_key:
        print("❌ MODELRED_API_KEY not found in .env file")
        return False

    client = ModelRed(api_key=api_key)
    print("✅ ModelRed client initialized")

    # Test 1: List all probes
    print_section("2.1: List All Probes")
    try:
        all_probes = client.list_probes()
        print(f"✅ Found {len(all_probes.probes)} total probes (filtered by your tier)")
        print(f"\nSample probes:")
        for i, probe in enumerate(all_probes.probes[:5], 1):
            print(f"   {i}. {probe.display_name}")
            print(f"      - Key: {probe.key}")
            print(f"      - Category: {probe.category}")
            print(f"      - Severity: {probe.severity}")
            print(f"      - Tier: {probe.tier}")
    except Exception as e:
        print(f"❌ Error listing all probes: {e}")
        return False

    # Test 2: Filter by severity - critical
    print_section("2.2: Filter by Severity (Critical)")
    try:
        critical_probes = client.list_probes(severity="critical")
        print(f"✅ Found {len(critical_probes.probes)} critical severity probes")
        for i, probe in enumerate(critical_probes.probes[:3], 1):
            print(f"   {i}. {probe.display_name} - {probe.severity}")
    except Exception as e:
        print(f"❌ Error filtering by critical severity: {e}")
        return False

    # Test 3: Filter by severity - high
    print_section("2.3: Filter by Severity (High)")
    try:
        high_probes = client.list_probes(severity="high")
        print(f"✅ Found {len(high_probes.probes)} high severity probes")
        for i, probe in enumerate(high_probes.probes[:3], 1):
            print(f"   {i}. {probe.display_name} - {probe.severity}")
    except Exception as e:
        print(f"❌ Error filtering by high severity: {e}")
        return False

    # Test 4: Filter by category - prompt_injection
    print_section("2.4: Filter by Category (prompt_injection)")
    try:
        injection_probes = client.list_probes(category="prompt_injection")
        print(f"✅ Found {len(injection_probes.probes)} prompt injection probes")
        for i, probe in enumerate(injection_probes.probes[:3], 1):
            print(f"   {i}. {probe.display_name} - {probe.category}")
    except Exception as e:
        print(f"❌ Error filtering by category: {e}")
        return False

    # Test 5: Filter by category - jailbreaks
    print_section("2.5: Filter by Category (jailbreaks)")
    try:
        jailbreak_probes = client.list_probes(category="jailbreaks")
        print(f"✅ Found {len(jailbreak_probes.probes)} jailbreak probes")
        for i, probe in enumerate(jailbreak_probes.probes[:3], 1):
            print(f"   {i}. {probe.display_name} - {probe.category}")
    except Exception as e:
        print(f"❌ Error filtering by jailbreaks: {e}")
        return False

    # Test 6: Combine category + severity
    print_section("2.6: Combine Category + Severity")
    try:
        combined = client.list_probes(category="prompt_injection", severity="critical")
        print(f"✅ Found {len(combined.probes)} critical prompt injection probes")
        for i, probe in enumerate(combined.probes[:3], 1):
            print(f"   {i}. {probe.display_name}")
            print(f"      - Category: {probe.category}")
            print(f"      - Severity: {probe.severity}")
    except Exception as e:
        print(f"❌ Error combining filters: {e}")
        return False

    # Test 7: Check probe categories
    print_section("2.7: Available Probe Categories")
    try:
        probes = client.list_probes()
        categories = set(p.category for p in probes.probes)
        print(f"✅ Found {len(categories)} unique categories:")
        for cat in sorted(categories):
            count = len([p for p in probes.probes if p.category == cat])
            print(f"   - {cat}: {count} probes")
    except Exception as e:
        print(f"❌ Error checking categories: {e}")
        return False

    # Test 8: Check probe severities
    print_section("2.8: Available Probe Severities")
    try:
        probes = client.list_probes()
        severities = set(p.severity for p in probes.probes)
        print(f"✅ Found {len(severities)} unique severities:")
        for sev in ["critical", "high", "medium", "low"]:
            if sev in severities:
                count = len([p for p in probes.probes if p.severity == sev])
                print(f"   - {sev}: {count} probes")
    except Exception as e:
        print(f"❌ Error checking severities: {e}")
        return False

    # Cleanup
    client.close()
    print_section("✅ ALL PROBE DISCOVERY TESTS PASSED")
    return True


if __name__ == "__main__":
    try:
        success = test_probe_discovery()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
