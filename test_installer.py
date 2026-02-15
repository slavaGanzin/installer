"""Test the installer server to ensure it serves scripts with correct fallback logic."""

import subprocess
import time
import requests
import signal
import os
import sys


def test_installer_script_has_path_fallback():
    """Test that the installer script tries all PATH directories before ~/.local/bin"""

    # Start the installer server in background
    print("Starting installer server...")
    env = os.environ.copy()
    env["GH_TOKEN"] = ""  # No token needed for template test

    server = subprocess.Popen(
        ["./installer", "--port", "8765"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    # Give server time to start
    time.sleep(2)

    try:
        # Fetch the install script
        print("Fetching install script from server...")
        response = requests.get("http://localhost:8765/help-me-test/cli?type=script", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        script = response.text

        # Test 1: Script should handle permission denied
        assert "Permission denied" in script, (
            "Script missing permission denied handling"
        )
        print("✓ Permission denied handling found")

        # Test 2: Script should try PATH directories
        assert "IFS=" in script and "read -ra PATH_DIRS" in script, (
            "Script missing PATH directory iteration"
        )
        print("✓ PATH directory iteration found")

        # Test 3: Script should skip empty/relative paths and original failed dir
        assert (
            "Skip empty, relative paths" in script or 'if [ -z "$PATH_DIR" ]' in script
        ), "Script missing path validation"
        print("✓ PATH validation found")

        # Test 4: Script should fallback to ~/.local/bin
        assert 'LOCAL_BIN="$HOME/.local/bin"' in script, (
            "Script missing ~/.local/bin fallback"
        )
        print("✓ ~/.local/bin fallback found")

        # Test 5: Script should add to shell configs only when needed
        assert ".bashrc" in script and ".zshrc" in script, (
            "Script missing shell config modification"
        )
        print("✓ Shell config modification found")

        # Test 6: Script should support fish shell
        assert "fish_add_path" in script or "*fish*" in script, (
            "Script missing fish shell support"
        )
        print("✓ Fish shell support found")

        # Test 7: Script should check for duplicates before adding to PATH
        assert "grep -q" in script and ".local/bin" in script, (
            "Script missing duplicate prevention"
        )
        print("✓ Duplicate prevention found")

        # Test 8: Verify logic order - try PATH before creating ~/.local/bin
        path_try_pos = script.find("IFS=")
        local_bin_pos = script.find('LOCAL_BIN="$HOME/.local/bin"')
        assert path_try_pos < local_bin_pos, (
            "Script tries ~/.local/bin before PATH directories"
        )
        print("✓ Correct fallback order (PATH first, then ~/.local/bin)")

        print("\n✅ All installer script tests passed!")

    finally:
        # Stop the server
        print("\nStopping installer server...")
        server.send_signal(signal.SIGTERM)
        server.wait(timeout=5)


if __name__ == "__main__":
    test_installer_script_has_path_fallback()
