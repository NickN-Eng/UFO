"""
Azure AD Authentication Test Script for Azure OpenAI
Tests the same authentication flow used by the UFO project with detailed debugging.
"""

import os
import sys
import shutil
from typing import Optional, Callable

# Configuration - matching your UFO config.yaml
TENANT_ID = "5f8bc481-8908-47bf-9c84-c3ef37fe8c16"
AZURE_ENDPOINT = "https://nicholasniem-9000-resource.cognitiveservices.azure.com/"
API_VERSION = "2024-12-01-preview"
MODEL_DEPLOYMENT = "gpt-5-mini"
SCOPE_BASE = "https://cognitiveservices.azure.com"


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_azure_identity_imports():
    """Test if required Azure Identity packages are installed"""
    print_section("Step 1: Testing Azure Identity Package Installation")

    try:
        import azure.identity
        print(f"[OK] azure-identity package installed: version {azure.identity.__version__}")
    except ImportError as e:
        print(f"[X] ERROR: azure-identity package not installed")
        print(f"  Install with: pip install azure-identity")
        return False

    try:
        from azure.identity.broker import InteractiveBrowserBrokerCredential
        print(f"[OK] azure-identity-broker package installed (InteractiveBrowserBrokerCredential available)")
    except ImportError:
        print(f"[!] WARNING: azure-identity-broker not installed")
        print(f"  Interactive browser authentication may not work optimally")
        print(f"  Install with: pip install azure-identity-broker")

    try:
        import msal
        print(f"[OK] msal package installed: version {msal.__version__}")
    except ImportError:
        print(f"[X] WARNING: msal package not installed")
        print(f"  Install with: pip install msal")

    return True


def test_openai_package():
    """Test if OpenAI package is installed"""
    print_section("Step 2: Testing OpenAI Package Installation")

    try:
        import openai
        print(f"[OK] openai package installed: version {openai.__version__}")
        return True
    except ImportError:
        print(f"[X] ERROR: openai package not installed")
        print(f"  Install with: pip install openai")
        return False


def detect_authentication_method():
    """Detect which authentication method will be used"""
    print_section("Step 3: Detecting Available Authentication Methods")

    methods = []

    # Check for Azure CLI
    az_path = shutil.which("az")
    if az_path:
        print(f"[OK] Azure CLI found at: {az_path}")
        methods.append("azure_cli")
    else:
        print(f"[X] Azure CLI not found in PATH")

    # Check platform for broker authentication
    if sys.platform.startswith("win32"):
        print(f"[OK] Windows detected - InteractiveBrowserBrokerCredential available")
        methods.append("interactive_browser_broker")
    elif sys.platform.startswith("darwin"):
        print(f"[OK] macOS detected - InteractiveBrowserBrokerCredential available")
        methods.append("interactive_browser_broker")
    elif os.environ.get("WSL_DISTRO_NAME", ""):
        print(f"[OK] WSL detected - InteractiveBrowserBrokerCredential available")
        methods.append("interactive_browser_broker")
    elif os.environ.get("TERM_PROGRAM", "") == "vscode":
        print(f"[OK] VS Code terminal detected - InteractiveBrowserBrokerCredential available")
        methods.append("interactive_browser_broker")
    else:
        print(f"[!] Platform: {sys.platform} - May fall back to DeviceCodeCredential")
        methods.append("device_code")

    print(f"\nAuthentication methods available: {', '.join(methods)}")
    return methods


def create_token_provider(use_azure_cli: bool = False, preferred_method: Optional[str] = None) -> Optional[Callable[[], str]]:
    """Create a token provider using Azure Identity"""
    print_section("Step 4: Creating Token Provider")

    try:
        from azure.identity import (
            AzureCliCredential,
            DeviceCodeCredential,
            TokenCachePersistenceOptions,
            get_bearer_token_provider,
        )

        scope = f"{SCOPE_BASE}/.default"
        print(f"Target scope: {scope}")
        print(f"Tenant ID: {TENANT_ID}")

        # Token cache configuration
        token_cache_file = "azure-ad-test-cache.bin"
        token_cache_option = TokenCachePersistenceOptions(
            name=token_cache_file,
            enable_persistence=True,
            allow_unencrypted_storage=True,
        )
        print(f"Token cache file: {token_cache_file}")

        # Try Azure CLI first if available
        if use_azure_cli or (preferred_method == "cli" and shutil.which("az") is not None):
            print(f"\n-> Attempting AzureCliCredential authentication...")
            try:
                credential = AzureCliCredential(tenant_id=TENANT_ID)
                token_provider = get_bearer_token_provider(credential, scope)

                # Test token acquisition
                print(f"  Testing token acquisition...")
                token = token_provider()
                print(f"[OK] Successfully acquired token via Azure CLI")
                print(f"  Token (first 50 chars): {token[:50]}...")
                return token_provider
            except Exception as e:
                print(f"[X] Azure CLI authentication failed: {e}")
                print(f"  Tip: Try running 'az login --tenant {TENANT_ID}'")

        # Use Device Code if explicitly requested
        if preferred_method == "device":
            print(f"\n-> User selected DeviceCodeCredential authentication...")
            # Skip to device code section
            pass
        # Fall back to Interactive Browser Broker on Windows
        elif preferred_method == "browser" or (preferred_method is None and (sys.platform.startswith("win32") or sys.platform.startswith("darwin"))):
            print(f"\n-> Attempting InteractiveBrowserBrokerCredential authentication...")
            print(f"  NOTE: If this hangs, try using DeviceCodeCredential instead (press Ctrl+C)")
            try:
                from azure.identity.broker import InteractiveBrowserBrokerCredential
                import msal
                import threading

                credential = InteractiveBrowserBrokerCredential(
                    tenant_id=TENANT_ID,
                    cache_persistence_options=token_cache_option,
                    use_default_broker_account=False,  # Changed to False to force interactive login
                    parent_window_handle=msal.PublicClientApplication.CONSOLE_WINDOW_HANDLE,
                    timeout=60,  # 60 second timeout
                )

                # Authenticate interactively with timeout
                print(f"  Initiating interactive authentication...")
                print(f"  [!] A browser window SHOULD open for you to sign in")
                print(f"  [!] Timeout: 35 seconds")

                auth_result = [None]
                error_result = [None]

                def authenticate_with_timeout():
                    try:
                        auth_result[0] = credential.authenticate(scopes=[scope])
                    except Exception as e:
                        error_result[0] = e

                auth_thread = threading.Thread(target=authenticate_with_timeout)
                auth_thread.daemon = True
                auth_thread.start()
                auth_thread.join(timeout=35)  # Wait 35 seconds

                if auth_thread.is_alive():
                    print(f"[X] Interactive browser authentication timed out after 60 seconds")
                    print(f"  This usually means the browser dialog didn't appear")
                    print(f"  Falling back to DeviceCodeCredential...")
                elif error_result[0]:
                    raise error_result[0]
                elif auth_result[0]:
                    print(f"[OK] Interactive authentication successful")
                    print(f"  Username: {auth_result[0].username}")
                    print(f"  Authority: {auth_result[0].authority}")

                    token_provider = get_bearer_token_provider(credential, scope)

                    # Test token acquisition
                    token = token_provider()
                    print(f"[OK] Successfully acquired token via Interactive Browser")
                    print(f"  Token (first 50 chars): {token[:50]}...")
                    return token_provider

            except ImportError:
                print(f"[X] InteractiveBrowserBrokerCredential not available")
                print(f"  Install with: pip install azure-identity-broker")
            except Exception as e:
                print(f"[X] Interactive browser authentication failed: {e}")
                print(f"  Error type: {type(e).__name__}")

        # Fall back to Device Code
        print(f"\n-> Attempting DeviceCodeCredential authentication...")
        try:
            credential = DeviceCodeCredential(
                tenant_id=TENANT_ID,
                cache_persistence_options=token_cache_option,
            )

            print(f"  Initiating device code authentication...")
            print(f"  [!] You will be prompted with a code to enter at microsoft.com/devicelogin")
            auth_record = credential.authenticate(scopes=[scope])

            if auth_record:
                print(f"[OK] Device code authentication successful")
                print(f"  Username: {auth_record.username}")

            token_provider = get_bearer_token_provider(credential, scope)

            # Test token acquisition
            token = token_provider()
            print(f"[OK] Successfully acquired token via Device Code")
            print(f"  Token (first 50 chars): {token[:50]}...")
            return token_provider

        except Exception as e:
            print(f"[X] Device code authentication failed: {e}")

        return None

    except Exception as e:
        print(f"[X] CRITICAL ERROR creating token provider: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_azure_openai_connection(token_provider: Callable[[], str]):
    """Test connection to Azure OpenAI using the token provider"""
    print_section("Step 5: Testing Azure OpenAI Connection")

    try:
        from openai import AzureOpenAI

        print(f"Creating AzureOpenAI client...")
        print(f"  Endpoint: {AZURE_ENDPOINT}")
        print(f"  API Version: {API_VERSION}")
        print(f"  Model Deployment: {MODEL_DEPLOYMENT}")

        client = AzureOpenAI(
            api_version=API_VERSION,
            azure_endpoint=AZURE_ENDPOINT,
            azure_ad_token_provider=token_provider,
        )

        print(f"[OK] AzureOpenAI client created successfully")

        # Test a simple completion
        print(f"\n-> Testing chat completion with model: {MODEL_DEPLOYMENT}")
        print(f"  Sending test message: 'Say hello in one word'")

        response = client.chat.completions.create(
            model=MODEL_DEPLOYMENT,
            messages=[
                {"role": "user", "content": "Say hello in one word"}
            ],
            max_completion_tokens=500,  # GPT-5 reasoning models need higher limits (use hundreds of tokens for internal reasoning)
            reasoning_effort="low",  # Options: minimal, low, medium, high (minimal=fastest, high=most thorough)
            # Note: GPT-5 models don't support custom temperature values, only default (1) is supported
        )

        print(f"\n[OK] SUCCESS! Chat completion received:")

        # Debug: Print full response structure
        print(f"\n[DEBUG] Full response structure:")
        print(f"  Response type: {type(response)}")
        print(f"  Number of choices: {len(response.choices)}")

        message = response.choices[0].message
        content = message.content

        # Print all message attributes
        print(f"\n[DEBUG] Message attributes:")
        for attr in dir(message):
            if not attr.startswith('_'):
                try:
                    value = getattr(message, attr)
                    if not callable(value):
                        print(f"  {attr}: {value}")
                except Exception:
                    pass

        print(f"\n[RESULT]")
        print(f"  Response Content: '{content if content else '(empty)'}'")
        print(f"  Content Type: {type(content)}")
        print(f"  Content Length: {len(content) if content else 0}")
        print(f"  Model: {response.model}")
        print(f"  Usage: {response.usage.prompt_tokens} prompt tokens, {response.usage.completion_tokens} completion tokens")
        print(f"  Finish Reason: {response.choices[0].finish_reason}")

        # Check if this is actually a problem
        if not content or len(content) == 0:
            print(f"\n[!] WARNING: Response content is empty!")
            print(f"  This may indicate a GPT-5 model issue or configuration problem")
            return False

        return True

    except Exception as e:
        print(f"\n[X] FAILED to connect to Azure OpenAI: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_azure_permissions():
    """Provide guidance on checking Azure permissions"""
    print_section("Step 6: Azure Permissions Check")

    print("To verify your Azure permissions:")
    print("\n1. Go to Azure Portal: https://portal.azure.com")
    print("2. Navigate to your Azure OpenAI resource:")
    print(f"   Resource: nicholasniem-9000-resource")
    print("3. Click 'Access control (IAM)' in the left menu")
    print("4. Click 'Check access' or 'Role assignments'")
    print("5. Verify your account has one of these roles:")
    print("   • Cognitive Services OpenAI User (for inference)")
    print("   • Cognitive Services OpenAI Contributor (full access)")
    print("   • Cognitive Services User (general access)")
    print("\n6. Verify the deployment exists:")
    print("   • Go to Azure OpenAI Studio: https://oai.azure.com/")
    print(f"   • Check that deployment '{MODEL_DEPLOYMENT}' exists")
    print("   • Verify it's using the gpt-5-mini model")


def main():
    """Main test execution"""
    print("\n" + "=" * 80)
    print("  AZURE AD AUTHENTICATION TEST FOR AZURE OPENAI")
    print("  Testing UFO Project Configuration")
    print("=" * 80)

    print(f"\nConfiguration:")
    print(f"  Tenant ID: {TENANT_ID}")
    print(f"  Endpoint: {AZURE_ENDPOINT}")
    print(f"  Model: {MODEL_DEPLOYMENT}")
    print(f"  API Version: {API_VERSION}")
    print(f"  Scope: {SCOPE_BASE}/.default")

    # Step 1: Check packages
    if not test_azure_identity_imports():
        print("\n[FAIL] FATAL: Required packages not installed")
        return 1

    # Step 2: Check OpenAI package
    if not test_openai_package():
        print("\n[FAIL] FATAL: OpenAI package not installed")
        return 1

    # Step 3: Detect authentication methods
    methods = detect_authentication_method()

    # Ask user for preferred authentication method
    print("\n" + "=" * 80)
    print("  Select Authentication Method")
    print("=" * 80)
    print("\nAvailable authentication methods:")

    az_available = shutil.which("az") is not None
    if az_available:
        print("  1. Azure CLI (recommended - fastest and most reliable)")
    print("  2. Interactive Browser (may hang on some systems)")
    print("  3. Device Code (most reliable, requires manual browser login)")

    while True:
        try:
            if az_available:
                choice = input("\nEnter your choice (1-3) [default: 3]: ").strip()
                if not choice:
                    choice = "3"
            else:
                choice = input("\nEnter your choice (2-3) [default: 3]: ").strip()
                if not choice:
                    choice = "3"

            if choice == "1" and az_available:
                preferred_method = "cli"
                break
            elif choice == "2":
                preferred_method = "browser"
                print("\n[!] WARNING: Interactive Browser may hang on some systems.")
                print("    If it hangs for more than 35 seconds, it will automatically fall back to Device Code.")
                confirm = input("    Continue with Interactive Browser? (y/n) [default: y]: ").strip().lower()
                if not confirm or confirm == 'y':
                    break
            elif choice == "3":
                preferred_method = "device"
                break
            else:
                print("[!] Invalid choice. Please try again.")
        except KeyboardInterrupt:
            print("\n\n[!] User cancelled selection")
            return 130

    # Step 4: Create token provider
    token_provider = create_token_provider(preferred_method=preferred_method)
    if not token_provider:
        print("\n[FAIL] FATAL: Could not create token provider")
        check_azure_permissions()
        return 1

    # Step 5: Test Azure OpenAI connection
    success = test_azure_openai_connection(token_provider)

    # Step 6: Permissions check (if connection failed)
    if not success:
        check_azure_permissions()

    # Final result
    print_section("FINAL RESULT")
    if success:
        print("[PASS] ALL TESTS PASSED!")
        print("\nYour Azure AD authentication is working correctly.")
        print("The UFO project should now work with these credentials.")
        return 0
    else:
        print("[FAIL] TESTS FAILED")
        print("\nPlease review the errors above and:")
        print("1. Ensure you have the correct Azure permissions")
        print("2. Verify the deployment name and model are correct")
        print("3. Check that you're logged in to the correct tenant")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[!] Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n[FAIL] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
