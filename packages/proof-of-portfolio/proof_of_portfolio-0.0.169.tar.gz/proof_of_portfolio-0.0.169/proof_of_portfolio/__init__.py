# This file makes the src directory a Python package

import os
import shutil
import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import wraps
import subprocess
from pathlib import Path
import json
import time
import traceback
import bittensor as bt
import threading

BB_PATH = os.path.expanduser("~/.bb/bb")
NARGO_PATH = os.path.expanduser("~/.nargo/bin/nargo")

# ruff: noqa
from .post_install import main as post_install_main
from .proof_generator import generate_proof
from .verifier import verify as verify


_dependencies_checked = False
_proof_lock = threading.Lock()
_background_executor = None


def ensure_dependencies():
    """Ensure bb and nargo are installed before running package functions."""
    global _dependencies_checked

    skip_install = os.environ.get("POP_SKIP_INSTALL", "").lower() in [
        "true",
        "1",
        "yes",
    ]
    if _dependencies_checked or skip_install:
        print(
            f"Dependencies checked: {_dependencies_checked}. Skip install: {skip_install}"
        )
        return

    missing_deps = []
    if not shutil.which("bb"):
        missing_deps.append("bb")
    if not shutil.which("nargo"):
        missing_deps.append("nargo")

    print(f"Missing deps: {missing_deps}")

    if missing_deps:
        print(f"Installing required dependencies: {', '.join(missing_deps)}...")
        print("This may take a few minutes on first run.")

        try:
            post_install_main()
            print("Dependencies installed successfully!")
        except Exception as e:
            print(f"Warning: Failed to install dependencies: {e}")

    _dependencies_checked = True


def requires_dependencies(func):
    """Decorator to ensure dependencies are installed before running a function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        ensure_dependencies()
        return func(*args, **kwargs)

    return wrapper


def _prove_worker(
    miner_data,
    daily_pnl=None,
    hotkey=None,
    verbose=False,
    vali_config=None,
    use_weighting=False,
    bypass_confidence=False,
    daily_checkpoints=2,
    account_size=None,
    witness_only=False,
    wallet=None,
    augmented_scores=None,
):
    """
    Worker function to run proof generation in a separate process.
    """
    try:
        result = generate_proof(
            data=miner_data,
            daily_pnl=daily_pnl,
            miner_hotkey=hotkey,
            verbose=verbose,
            vali_config=vali_config,
            use_weighting=use_weighting,
            bypass_confidence=bypass_confidence,
            daily_checkpoints=daily_checkpoints,
            account_size=account_size,
            witness_only=witness_only,
            wallet=wallet,
            augmented_scores=augmented_scores,
        )

        proof_results = result.get("proof_results", {})
        proof_generated = proof_results.get("proof_generated", False)

        if proof_generated:
            status = "success"
        else:
            status = "proof_generation_failed"

        return {
            "status": status,
            "portfolio_metrics": result.get("portfolio_metrics", {}),
            "merkle_roots": result.get("merkle_roots", {}),
            "data_summary": result.get("data_summary", {}),
            "proof_results": proof_results,
            "proof_generated": proof_generated,
        }

    except Exception as e:
        bt.logging.error(
            f"Exception in _prove_worker for hotkey {hotkey[:8] if hotkey else 'unknown'}: {type(e).__name__}: {e}"
        )
        bt.logging.error(f"Full traceback: {traceback.format_exc()}")

        return {
            "status": "error",
            "message": str(e),
            "proof_generated": False,
            "traceback": traceback.format_exc(),
        }


@requires_dependencies
async def prove(
    miner_data,
    daily_pnl=None,
    hotkey=None,
    verbose=False,
    vali_config=None,
    use_weighting=False,
    bypass_confidence=False,
    daily_checkpoints=2,
    account_size=None,
    witness_only=False,
    wallet=None,
    augmented_scores=None,
):
    """
    Generate zero-knowledge proof for miner portfolio data asynchronously.

    Args:
        miner_data: Dictionary containing perf_ledgers and positions for the miner
        hotkey: Miner's hotkey
        verbose: Boolean to control logging verbosity

    Returns:
        Dictionary with proof results including status, portfolio_metrics, etc.
    """
    loop = asyncio.get_event_loop()

    with ProcessPoolExecutor(max_workers=1) as executor:
        try:
            result = await loop.run_in_executor(
                executor,
                _prove_worker,
                miner_data,
                daily_pnl,
                hotkey,
                verbose,
                vali_config,
                use_weighting,
                bypass_confidence,
                daily_checkpoints,
                account_size,
                witness_only,
                wallet,
            )
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "proof_generated": False,
            }


def save_instant_mdd_results(results, hotkey):
    """
    Save instant MDD proof results to disk in ~/.pop/instant_mdd/ directory.

    Args:
        results: The instant MDD results dictionary to save
        hotkey: The miner's hotkey for filename
    """
    try:
        pop_dir = Path.home() / ".pop" / "instant_mdd"
        pop_dir.mkdir(parents=True, exist_ok=True)

        timestamp = int(time.time())
        filename = f"{hotkey}_{timestamp}.json"
        filepath = pop_dir / filename

        with open(filepath, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"Instant MDD results saved to {filepath}")
        return str(filepath)

    except Exception as e:
        print(f"Error saving instant MDD results: {str(e)}")
        return None


def get_latest_instant_mdd_for_miner(hotkey):
    """
    Get the latest instant MDD result for a specific miner.

    Args:
        hotkey: The miner's hotkey

    Returns:
        dict with latest instant MDD result, or None if not found
    """
    try:
        pop_dir = Path.home() / ".pop" / "instant_mdd"
        if not pop_dir.exists():
            return None

        matching_files = list(pop_dir.glob(f"{hotkey}_*.json"))
        if not matching_files:
            return None

        latest_file = max(matching_files, key=lambda f: f.stat().st_mtime)

        with open(latest_file, "r") as f:
            results = json.load(f)

        return results

    except Exception as e:
        print(f"Error getting latest instant MDD for {hotkey}: {str(e)}")
        return None


def get_all_instant_mdd_for_miner(hotkey):
    """
    Get all instant MDD results for a specific miner.

    Args:
        hotkey: The miner's hotkey

    Returns:
        list of instant MDD result dictionaries sorted by timestamp (newest first)
    """
    try:
        pop_dir = Path.home() / ".pop" / "instant_mdd"
        if not pop_dir.exists():
            return []

        matching_files = list(pop_dir.glob(f"{hotkey}_*.json"))
        if not matching_files:
            return []

        results = []
        for file_path in matching_files:
            try:
                with open(file_path, "r") as f:
                    result = json.load(f)
                    result["_filepath"] = str(file_path)
                    result["_timestamp"] = int(file_path.stem.split("_")[1])
                    results.append(result)
            except Exception as e:
                print(f"Error reading {file_path}: {str(e)}")
                continue

        return sorted(results, key=lambda x: x["_timestamp"], reverse=True)

    except Exception as e:
        print(f"Error getting all instant MDD for {hotkey}: {str(e)}")
        return []


@requires_dependencies
def prove_instant_mdd(hotkey, ledger_element):
    """
    Generate zero-knowledge proof for instant maximum drawdown calculation.

    Args:
        hotkey: Miner's hotkey for identification
        ledger_element: PerfLedger object containing checkpoint data

    Returns:
        Dictionary with proof results including drawdown calculation
    """

    SCALE = 10_000_000
    MAX_ARRAY_SIZE = 1024

    # Extract MDD values from ledger checkpoints
    if (
        not ledger_element
        or not hasattr(ledger_element, "cps")
        or len(ledger_element.cps) == 0
    ):
        return {
            "status": "no_data",
            "hotkey": hotkey,
            "exceeds_threshold": False,
            "drawdown_percentage": 0,
        }

    # Convert checkpoint MDD values to scaled integers
    mdd_values = []
    for cp in ledger_element.cps:
        if hasattr(cp, "mdd"):
            scaled_mdd = int(cp.mdd * SCALE)
            mdd_values.append(scaled_mdd)

    # Pad array to MAX_ARRAY_SIZE
    while len(mdd_values) < MAX_ARRAY_SIZE:
        mdd_values.append(0)

    n_checkpoints = min(len(ledger_element.cps), MAX_ARRAY_SIZE)

    # 10% threshold (from ValiConfig.DRAWDOWN_MAXVALUE_PERCENTAGE)
    max_drawdown_threshold = 10  # 10% as integer

    try:
        # Get the instant_mdd circuit path
        circuit_path = Path(__file__).parent.parent / "instant_mdd"

        # Create Prover.toml with input data
        prover_toml_path = circuit_path / "Prover.toml"
        with open(prover_toml_path, "w") as f:
            f.write(f'hotkey = "{hotkey}"\n')
            f.write(f"mdd_values = {mdd_values}\n")
            f.write(f'n_checkpoints = "{n_checkpoints}"\n')
            f.write(f'max_drawdown_threshold = "{max_drawdown_threshold}"\n')

        # Execute nargo
        result = subprocess.run(
            ["nargo", "execute"], capture_output=True, text=True, cwd=str(circuit_path)
        )

        if result.returncode != 0:
            return {
                "status": "execution_failed",
                "hotkey": hotkey,
                "error": result.stderr,
            }

        # Parse output
        if "Circuit output:" in result.stdout:
            output_line = result.stdout.split("Circuit output: ")[1].strip()

            # Parse tuple output (exceeds_threshold, drawdown_percentage)
            if output_line.startswith("(") and output_line.endswith(")"):
                output_line = output_line[1:-1]  # Remove parentheses
                parts = output_line.split(", ")
                if len(parts) == 2:
                    exceeds_threshold = parts[0].strip() == "true"
                    drawdown_percentage = int(
                        parts[1].strip()
                    )  # Already unscaled from circuit

                    results = {
                        "status": "success",
                        "hotkey": hotkey,
                        "exceeds_threshold": exceeds_threshold,
                        "drawdown_percentage": drawdown_percentage,
                        "n_checkpoints": n_checkpoints,
                    }

                    save_instant_mdd_results(results, hotkey)
                    return results

        return {"status": "parse_failed", "hotkey": hotkey, "raw_output": result.stdout}

    except Exception as e:
        return {"status": "error", "hotkey": hotkey, "message": str(e)}


def _get_background_executor():
    """Get or create the singleton background executor for proof generation."""
    global _background_executor
    if _background_executor is None:
        _background_executor = ThreadPoolExecutor(max_workers=1)
    return _background_executor


def _background_prove_worker(
    miner_data,
    daily_pnl,
    hotkey,
    verbose,
    vali_config,
    use_weighting,
    bypass_confidence,
    daily_checkpoints,
    account_size,
    witness_only,
    wallet,
    augmented_scores,
):
    """
    Worker that runs in background thread and acquires lock before proving.
    Calls generate_proof directly (not via ProcessPoolExecutor) so the lock
    properly serializes bb prove execution.

    This blocks until the lock is acquired, ensuring proofs are queued and
    processed sequentially.
    """
    bt.logging.info(
        f"Background proof worker starting for {hotkey[:8] if hotkey else 'unknown'}..."
    )

    with _proof_lock:
        bt.logging.info(
            f"Lock acquired for {hotkey[:8] if hotkey else 'unknown'}, starting proof generation..."
        )

        try:
            result = generate_proof(
                data=miner_data,
                daily_pnl=daily_pnl,
                miner_hotkey=hotkey,
                verbose=verbose,
                vali_config=vali_config,
                use_weighting=use_weighting,
                bypass_confidence=bypass_confidence,
                daily_checkpoints=daily_checkpoints,
                account_size=account_size,
                witness_only=witness_only,
                wallet=wallet,
                augmented_scores=augmented_scores,
            )

            proof_results = result.get("proof_results", {})
            proof_generated = proof_results.get("proof_generated", False)

            if proof_generated:
                status = "success"
            else:
                status = "proof_generation_failed"

            final_result = {
                "status": status,
                "portfolio_metrics": result.get("portfolio_metrics", {}),
                "merkle_roots": result.get("merkle_roots", {}),
                "data_summary": result.get("data_summary", {}),
                "proof_results": proof_results,
                "proof_generated": proof_generated,
            }

            bt.logging.info(
                f"Proof generation completed for {hotkey[:8] if hotkey else 'unknown'}: {final_result.get('status')}"
            )
            return final_result

        except Exception as e:
            bt.logging.error(
                f"Error in background proof worker for {hotkey[:8] if hotkey else 'unknown'}: {type(e).__name__}: {e}"
            )
            bt.logging.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e),
                "proof_generated": False,
                "traceback": traceback.format_exc(),
            }
        finally:
            bt.logging.info(f"Lock released for {hotkey[:8] if hotkey else 'unknown'}")


@requires_dependencies
def prove_sync(
    miner_data,
    daily_pnl=None,
    hotkey=None,
    verbose=False,
    vali_config=None,
    use_weighting=False,
    bypass_confidence=False,
    daily_checkpoints=2,
    account_size=None,
    witness_only=False,
    wallet=None,
    augmented_scores=None,
):
    """
    Synchronous wrapper for the prove function for backward compatibility.

    Args:
        miner_data: Dictionary containing perf_ledgers and positions for the miner
        hotkey: Miner's hotkey
        verbose: Boolean to control logging verbosity

    Returns:
        Dictionary with proof results including status, portfolio_metrics, etc.
    """
    return _prove_worker(
        miner_data,
        daily_pnl=daily_pnl,
        hotkey=hotkey,
        verbose=verbose,
        vali_config=vali_config,
        use_weighting=use_weighting,
        bypass_confidence=bypass_confidence,
        daily_checkpoints=daily_checkpoints,
        account_size=account_size,
        witness_only=witness_only,
        wallet=wallet,
        augmented_scores=augmented_scores,
    )


@requires_dependencies
def prove_async(
    miner_data,
    daily_pnl=None,
    hotkey=None,
    verbose=False,
    vali_config=None,
    use_weighting=False,
    bypass_confidence=False,
    daily_checkpoints=2,
    account_size=None,
    witness_only=False,
    wallet=None,
    augmented_scores=None,
):
    """
    Asynchronous proof generation that runs in background without blocking.
    Uses a lock to ensure only one bb prove process runs at a time.

    This function returns immediately with a status indicating the proof was queued.
    The actual proof generation happens in the background, and results are saved to ~/.pop/

    Args:
        miner_data: Dictionary containing perf_ledgers and positions for the miner
        daily_pnl: Daily PnL values
        hotkey: Miner's hotkey
        verbose: Boolean to control logging verbosity
        vali_config: Validator configuration
        use_weighting: Whether to use weighting
        bypass_confidence: Whether to bypass confidence checks
        daily_checkpoints: Number of daily checkpoints
        account_size: Account size for the miner
        witness_only: If True, only generate witness without full proof
        wallet: Wallet for signing
        augmented_scores: Augmented scores dictionary

    Returns:
        Dictionary with immediate status indicating proof was queued
    """
    executor = _get_background_executor()

    bt.logging.info(
        f"Queueing background proof generation for {hotkey[:8] if hotkey else 'unknown'}..."
    )

    future = executor.submit(
        _background_prove_worker,
        miner_data,
        daily_pnl,
        hotkey,
        verbose,
        vali_config,
        use_weighting,
        bypass_confidence,
        daily_checkpoints,
        account_size,
        witness_only,
        wallet,
        augmented_scores,
    )

    return {
        "status": "queued",
        "message": f"Proof generation queued for {hotkey[:8] if hotkey else 'unknown'}",
        "proof_generated": False,
        "future": future,
    }
