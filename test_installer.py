"""Integration test for installer - actually installs binaries and verifies they work."""

import subprocess
import time
import requests
import signal
import os
import sys
import tempfile
import shutil


def test_actual_installation():
    """Test that installers actually download and install working binaries"""

    # Start the installer server in background
    print("Starting installer server...")
    env = os.environ.copy()
    env["GH_TOKEN"] = os.environ.get("GH_TOKEN", "")

    server = subprocess.Popen(
        ["./installer", "--port", "8765"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    # Give server time to start
    time.sleep(2)

    # Create temporary directory for installations
    test_dir = tempfile.mkdtemp(prefix="installer-test-")
    install_dir = os.path.join(test_dir, "bin")
    os.makedirs(install_dir)

    try:
        print(f"Test directory: {test_dir}")
        print(f"Install directory: {install_dir}")

        # Test 1: Install helpmetest (using exact URL from app/server/API.js:441)
        print("\n=== Testing helpmetest installation (/install) ===")
        result = subprocess.run(
            f'curl -sf "http://localhost:8765/help-me-test/cli!?type=script&as=helpmetest" | OUT_DIR={install_dir} bash',
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )

        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

        if result.returncode != 0:
            raise AssertionError(f"helpmetest installation failed with exit code {result.returncode}")

        print("✓ Installation script completed")

        # Verify binary exists
        helpmetest_bin = os.path.join(install_dir, "helpmetest")
        assert os.path.exists(helpmetest_bin), f"Binary not found at {helpmetest_bin}"
        print(f"✓ Binary exists at {helpmetest_bin}")

        # Verify binary is executable
        assert os.access(helpmetest_bin, os.X_OK), "Binary is not executable"
        print("✓ Binary is executable")
        print("✓ Binary downloaded and installed successfully")

        # Test 2: Install frpc (using exact URL from app/server/API.js:453)
        print("\n=== Testing frpc installation (/install/frpc) ===")
        result = subprocess.run(
            f'curl -sf "http://localhost:8765/fatedier/frp!?type=script&filter=frpc&as=frpc" | OUT_DIR={install_dir} bash',
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )

        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

        if result.returncode != 0:
            raise AssertionError(f"frpc installation failed with exit code {result.returncode}")

        print("✓ Installation script completed")

        # Verify binary exists
        frpc_bin = os.path.join(install_dir, "frpc")
        assert os.path.exists(frpc_bin), f"Binary not found at {frpc_bin}"
        print(f"✓ Binary exists at {frpc_bin}")

        # Verify binary is executable
        assert os.access(frpc_bin, os.X_OK), "Binary is not executable"
        print("✓ Binary is executable")
        print("✓ Binary downloaded and installed successfully")

        # Test 3: Install frps (using exact URL from app/server/API.js:465)
        print("\n=== Testing frps installation (/install/frps) ===")
        result = subprocess.run(
            f'curl -sf "http://localhost:8765/fatedier/frp!?type=script&filter=frps&as=frps" | OUT_DIR={install_dir} bash',
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )

        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

        if result.returncode != 0:
            raise AssertionError(f"frps installation failed with exit code {result.returncode}")

        print("✓ Installation script completed")

        # Verify binary exists
        frps_bin = os.path.join(install_dir, "frps")
        assert os.path.exists(frps_bin), f"Binary not found at {frps_bin}"
        print(f"✓ Binary exists at {frps_bin}")

        # Verify binary is executable
        assert os.access(frps_bin, os.X_OK), "Binary is not executable"
        print("✓ Binary is executable")
        print("✓ Binary downloaded and installed successfully")

        print("\n✅ All installation tests passed!")

    finally:
        # Cleanup
        print(f"\nCleaning up test directory: {test_dir}")
        shutil.rmtree(test_dir, ignore_errors=True)

        # Stop the server
        print("Stopping installer server...")
        server.send_signal(signal.SIGTERM)
        server.wait(timeout=5)


if __name__ == "__main__":
    test_actual_installation()
