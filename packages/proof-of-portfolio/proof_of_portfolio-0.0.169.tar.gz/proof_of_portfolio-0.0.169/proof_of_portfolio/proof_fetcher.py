import requests
import bittensor as bt
from typing import Optional, Dict, Any
from .verifier import verify


def get_validator_miner_proof(
    validator_hotkey: str,
    miner_hotkey: str,
    include_testnet: bool = False,
    api_base_url: str = "https://api.omron.ai",
) -> Optional[Dict[str, Any]]:
    """
    Fetch the latest proof for a specific miner from a validator.

    Args:
        validator_hotkey: The validator's hotkey who generated the proof
        miner_hotkey: The miner's hotkey whose portfolio was proven
        include_testnet: Whether to include testnet proofs
        api_base_url: Base URL for the API

    Returns:
        Dictionary containing proof data and decoded metrics, or None if not found
    """
    try:
        url = f"{api_base_url}/ptn/{validator_hotkey}"
        params = {"include_testnet": str(include_testnet).lower()}

        bt.logging.debug(
            f"Fetching proofs from {validator_hotkey[:8]}... for miner {miner_hotkey[:8]}..."
        )

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        proofs = data.get("proofs", [])

        for proof in proofs:
            decoded_signals = proof.get("decoded_signals", {})
            if decoded_signals.get("hotkey") == miner_hotkey:
                bt.logging.info(
                    f"Found proof for miner {miner_hotkey[:8]} from validator {validator_hotkey[:8]}"
                )
                return proof

        bt.logging.warning(
            f"No proof found for miner {miner_hotkey[:8]} from validator {validator_hotkey[:8]}"
        )
        return None

    except requests.exceptions.RequestException as e:
        bt.logging.error(
            f"Error fetching proof from validator {validator_hotkey[:8]}: {e}"
        )
        return None
    except Exception as e:
        bt.logging.error(f"Unexpected error fetching proof: {e}")
        return None


def fetch_and_verify_miner_proof(
    validator_hotkey: str,
    miner_hotkey: str,
    include_testnet: bool = False,
    api_base_url: str = "https://api.omron.ai",
) -> Optional[Dict[str, Any]]:
    """
    Fetch and verify a proof for a specific miner from a validator.

    Args:
        validator_hotkey: The validator's hotkey who generated the proof
        miner_hotkey: The miner's hotkey whose portfolio was proven
        include_testnet: Whether to include testnet proofs
        api_base_url: Base URL for the API

    Returns:
        Dictionary containing verified proof data and portfolio metrics, or None if verification fails
    """
    proof_data = get_validator_miner_proof(
        validator_hotkey, miner_hotkey, include_testnet, api_base_url
    )

    if not proof_data:
        return None

    proof_hex = proof_data.get("proof")
    public_inputs_hex = proof_data.get("public_signals")

    if not proof_hex or not public_inputs_hex:
        bt.logging.error(
            f"Missing proof or public_signals in API response for miner {miner_hotkey[:8]}"
        )
        return None

    bt.logging.info(
        f"Verifying proof for miner {miner_hotkey[:8]} from validator {validator_hotkey[:8]}..."
    )
    is_valid = verify(proof_hex, public_inputs_hex)

    if is_valid:
        bt.logging.info(
            f"Proof for miner {miner_hotkey[:8]} from validator {validator_hotkey[:8]} is verified"
        )
        return proof_data.get("decoded_signals", {})
    else:
        bt.logging.warning(
            f"Proof for miner {miner_hotkey[:8]} from validator {validator_hotkey[:8]} failed verification"
        )
        return None


def extract_portfolio_metrics(proof_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Extract portfolio metrics from a verified proof's decoded signals.

    Args:
        proof_data: The decoded signals from a verified proof

    Returns:
        Dictionary with portfolio metrics (sharpe, calmar, sortino, omega, etc.)
    """
    if not proof_data:
        return {}

    metrics = proof_data.get("portfolio_metrics", {})

    return {
        "avg_daily_pnl": metrics.get("avg_daily_pnl", 0.0),
        "sharpe_ratio": metrics.get("sharpe_ratio", 0.0),
        "daily_max_drawdown": metrics.get("daily_max_drawdown", 0.0),
        "calmar_ratio": metrics.get("calmar_ratio", 0.0),
        "omega_ratio": metrics.get("omega_ratio", 0.0),
        "sortino_ratio": metrics.get("sortino_ratio", 0.0),
        "statistical_confidence": metrics.get("statistical_confidence", 0.0),
        "returns_merkle_root": metrics.get("returns_merkle_root", ""),
        "signals_merkle_root": proof_data.get("signals_merkle_root", ""),
    }
