import os
import subprocess
import tempfile
import bittensor as bt
from . import BB_PATH


def verify(proof_hex, public_inputs_hex):
    """
    Verify a zero-knowledge proof using hex string data.

    Args:
        proof_hex (str): Hex string of proof data
        public_inputs_hex (str): Hex string of public inputs data

    Returns:
        bool: True if verification succeeds, False otherwise
    """

    try:
        proof_data = bytes.fromhex(proof_hex)
        public_inputs_data = bytes.fromhex(public_inputs_hex)
    except ValueError as e:
        bt.logging.error(f"Invalid hex data: {str(e)}")
        return False

    vk_path = os.path.join(os.path.dirname(__file__), "circuits", "vk", "vk")
    if not os.path.exists(vk_path):
        bt.logging.error(f"Verification key file not found: {vk_path}")
        return False

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            proof_path = os.path.join(temp_dir, "proof")
            public_inputs_path = os.path.join(temp_dir, "public_inputs")

            with open(proof_path, "wb") as f:
                f.write(proof_data)
            with open(public_inputs_path, "wb") as f:
                f.write(public_inputs_data)

            result = subprocess.run(
                [
                    BB_PATH,
                    "verify",
                    "-k",
                    vk_path,
                    "-p",
                    proof_path,
                    "-i",
                    public_inputs_path,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                bt.logging.info("Proof verification successful")
                if result.stdout:
                    print(f"DEBUG: bb verify stdout: {result.stdout}")
                return True
            else:
                bt.logging.error(f"Proof verification failed: {result.stderr}")
                print(f"DEBUG: bb verify failed with return code {result.returncode}")
                print(f"DEBUG: bb verify stdout: {result.stdout}")
                print(f"DEBUG: bb verify stderr: {result.stderr}")
                return False

    except subprocess.TimeoutExpired:
        bt.logging.error("Proof verification timed out")
        return False
    except Exception as e:
        bt.logging.error(f"Error during proof verification: {str(e)}")
        return False
