"""
Quick Azure AD Authentication Status Checker
Shows current authentication status without attempting to authenticate
"""

import os
import sys
import shutil
from pathlib import Path


def check_azure_cli_status():
    """Check if Azure CLI is installed and logged in"""
    print("=" * 60)
    print("AZURE CLI STATUS")
    print("=" * 60)

    az_path = shutil.which("az")

    if az_path:
        print(f"[OK] Azure CLI installed at: {az_path}")

        # Try to get current account info
        try:
            import subprocess
            result = subprocess.run(
                ["az", "account", "show"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                print(f"[OK] Azure CLI is logged in")
                import json
                account_info = json.loads(result.stdout)
                print(f"  Account: {account_info.get('user', {}).get('name', 'Unknown')}")
                print(f"  Tenant: {account_info.get('tenantId', 'Unknown')}")
                print(f"  Subscription: {account_info.get('name', 'Unknown')}")
                return True
            else:
                print(f"[X] Azure CLI not logged in")
                print(f"  Run: az login --tenant 5f8bc481-8908-47bf-9c84-c3ef37fe8c16")
                return False

        except Exception as e:
            print(f"[!] Could not check Azure CLI status: {e}")
            return False
    else:
        print(f"[X] Azure CLI not installed")
        print(f"  Install from: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False


def check_token_cache():
    """Check if authentication token cache exists"""
    print("\n" + "=" * 60)
    print("TOKEN CACHE STATUS")
    print("=" * 60)

    cache_files = [
        "aoai-token-cache.bin",  # UFO project cache
        "azure-ad-test-cache.bin",  # Test script cache
    ]

    found_any = False
    for cache_file in cache_files:
        if os.path.exists(cache_file):
            stat = os.stat(cache_file)
            size = stat.st_size
            print(f"[OK] Found cache: {cache_file}")
            print(f"  Size: {size} bytes")
            found_any = True

    if not found_any:
        print(f"[X] No token cache files found")
        print(f"  You will need to authenticate when running UFO")

    return found_any


def check_required_packages():
    """Check if required Python packages are installed"""
    print("\n" + "=" * 60)
    print("REQUIRED PACKAGES")
    print("=" * 60)

    packages = {
        "azure.identity": "azure-identity",
        "azure.identity.broker": "azure-identity-broker",
        "openai": "openai",
        "msal": "msal",
    }

    all_installed = True
    for module_name, package_name in packages.items():
        try:
            if module_name == "azure.identity.broker":
                from azure.identity.broker import InteractiveBrowserBrokerCredential
            else:
                __import__(module_name)
            print(f"[OK] {package_name} installed")
        except ImportError:
            print(f"[X] {package_name} NOT installed")
            print(f"  Install with: pip install {package_name}")
            all_installed = False

    return all_installed


def check_environment():
    """Check environment variables"""
    print("\n" + "=" * 60)
    print("ENVIRONMENT")
    print("=" * 60)

    print(f"Platform: {sys.platform}")
    print(f"Python: {sys.version.split()[0]}")

    env_vars = [
        "AZURE_TENANT_ID",
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET",
        "AZURE_AUTHORITY_HOST",
    ]

    found_any = False
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"[OK] {var} is set")
            found_any = True

    if not found_any:
        print(f"[i] No Azure environment variables set (this is normal for interactive auth)")


def provide_recommendations():
    """Provide recommendations based on checks"""
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)

    print("\nTo use Azure AD authentication with UFO:")
    print("\n1. EASIEST: Install and login to Azure CLI")
    print("   az login --tenant 5f8bc481-8908-47bf-9c84-c3ef37fe8c16")
    print("\n2. OR: Let UFO authenticate interactively")
    print("   - A browser window will open automatically")
    print("   - Sign in with your Microsoft account")
    print("   - Credentials will be cached for future use")
    print("\n3. Verify Azure permissions:")
    print("   - Go to Azure Portal -> Your OpenAI Resource -> IAM")
    print("   - Ensure you have 'Cognitive Services OpenAI User' role")
    print("\n4. Test authentication:")
    print("   python debug/azure_ad_test.py")


def main():
    """Main status check"""
    print("\n" + "=" * 60)
    print("  AZURE AD AUTHENTICATION STATUS CHECK")
    print("=" * 60)
    print()

    cli_ok = check_azure_cli_status()
    packages_ok = check_required_packages()
    cache_exists = check_token_cache()
    check_environment()
    provide_recommendations()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if cli_ok and packages_ok:
        print("[PASS] Ready to use Azure AD authentication!")
        print("   Azure CLI is logged in and packages are installed.")
        return 0
    elif packages_ok and cache_exists:
        print("[PASS] Likely ready to use Azure AD authentication")
        print("   Packages installed and cached credentials found.")
        return 0
    elif packages_ok:
        print("[!] Packages installed, but no authentication detected")
        print("   Run azure_ad_test.py to authenticate")
        return 1
    else:
        print("[FAIL] Missing required packages")
        print("   Install packages then authenticate")
        return 1


if __name__ == "__main__":
    sys.exit(main())
