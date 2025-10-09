import subprocess
import toml
import re
import os
import time
import json
import math
import logging
import bittensor as bt
import traceback
import requests
import base64
from pathlib import Path

# Import global constants
from . import BB_PATH, NARGO_PATH


ARRAY_SIZE = 256
MAX_DAYS = 256
MAX_SIGNALS = 512
MERKLE_DEPTH = 8
SCALE = 10**8  # Base scaling factor (10^8) - used for all ratio outputs
PRIME = 21888242871839275222246405745257275088548364400416034343698204186575808495617


def setup_proof_logging(hotkey):
    log_dir = Path.home() / ".pop"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"{hotkey[:16]}_proof_log.log"

    logger = logging.getLogger(f"pop.proof.{hotkey[:8]}")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

    return logger, log_file


def log_verbose(verbose, level, message, logger=None):
    if logger:
        getattr(logger, level.lower())(message)
    if verbose:
        getattr(bt.logging, level)(message)


def get_attr(obj, attr):
    """Get attribute from object or dictionary"""
    return getattr(obj, attr) if hasattr(obj, attr) else obj[attr]


def scale_to_int(value):
    """Convert float to scaled integer"""
    return int(value * SCALE)


def scale_from_int(value):
    """Convert scaled integer back to float"""
    return value / SCALE


def run_command(command, cwd, logger=None):
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        msg = f"Command failed: {' '.join(command)}"
        if logger:
            logger.error(msg)
            logger.error(f"stdout: {result.stdout}")
            logger.error(f"stderr: {result.stderr}")
        bt.logging.error(msg)
        bt.logging.error(f"stdout: {result.stdout}")
        bt.logging.error(f"stderr: {result.stderr}")
        raise RuntimeError(
            f"Command {' '.join(command)} failed with exit code {result.returncode}"
        )
    return result.stdout


def parse_circuit_output(output):
    if "[" in output and "]" in output and "MerkleTree" not in output:
        array_matches = re.findall(r"\[([^\]]+)\]", output)
        if array_matches:
            array_content = array_matches[-1]
            values = []
            for item in array_content.split(","):
                item = item.strip()
                if item.startswith("0x"):
                    try:
                        values.append(str(int(item, 16)))
                    except ValueError:
                        continue
                elif item.lstrip("-").isdigit():
                    values.append(item)
            if values:
                return values

    struct_start = output.find("{")
    struct_end = output.rfind("}")

    if struct_start == -1 or struct_end == -1:
        return re.findall(r"Field\(([-0-9]+)\)", output)

    struct_content = output[struct_start : struct_end + 1]

    if "MerkleTree" in output:
        tree = {}
        if "path_elements:" in struct_content:
            start = struct_content.find("path_elements:") + len("path_elements:")
            end = struct_content.find(", path_indices:")
            path_elem_section = struct_content[start:end].strip()
            tree["path_elements"] = parse_nested_arrays(path_elem_section)

        if "path_indices:" in struct_content:
            start = struct_content.find("path_indices:") + len("path_indices:")
            end = struct_content.find(", root:")
            path_idx_section = struct_content[start:end].strip()
            tree["path_indices"] = parse_nested_arrays(path_idx_section)

        if "root:" in struct_content:
            start = struct_content.find("root:") + len("root:")
            root_section = struct_content[start:].strip().rstrip("}")
            tree["root"] = root_section.strip()

        return tree

    values = []
    parts = re.split(r"[,\s]+", struct_content)
    for part in parts:
        part = part.strip("{}[](), \t\n\r")
        if not part:
            continue
        if part.startswith("0x") and len(part) > 2:
            try:
                values.append(str(int(part, 16)))
                continue
            except ValueError:
                pass
        if part.lstrip("-").isdigit():
            values.append(part)

    return values


def parse_nested_arrays(section):
    if not section.strip().startswith("["):
        return []

    arrays = []
    depth = 0
    current_array = ""

    for char in section:
        if char == "[":
            depth += 1
            if depth == 2:
                current_array = ""
            elif depth == 1:
                continue
        elif char == "]":
            depth -= 1
            if depth == 1:
                if current_array.strip():
                    arrays.append(
                        [x.strip() for x in current_array.split(",") if x.strip()]
                    )
                current_array = ""
            elif depth == 0:
                break
        elif depth == 2:
            current_array += char

    return arrays


def field_to_toml_value(f):
    return str(f + PRIME) if f < 0 else str(f)


def field_to_signed_int(field_str):
    val = int(field_str, 16) if field_str.startswith("0x") else int(field_str)
    return val - 2**64 if val >= 2**63 else val


def upload_proof(proof_hex, public_inputs_hex, wallet, testnet=True):
    """
    Upload proof to the API endpoint.

    Args:
        proof_hex: Proof as hex string
        public_inputs_hex: Public inputs as hex string
        wallet: Bittensor wallet for signing
        testnet: Whether this is a testnet proof

    Returns:
        API response dictionary or None if failed
    """
    bt.logging.info(
        f"[UPLOAD] Starting upload_proof: wallet={bool(wallet)}, proof_hex={bool(proof_hex)}, public_inputs_hex={bool(public_inputs_hex)}, testnet={testnet}"
    )

    if not wallet:
        bt.logging.warning("[UPLOAD] Missing wallet for upload")
        return None
    if not proof_hex:
        bt.logging.warning("[UPLOAD] Missing proof_hex for upload")
        return None
    if not public_inputs_hex:
        bt.logging.warning("[UPLOAD] Missing public_inputs_hex for upload")
        return None

    try:
        # Sign timestamp
        bt.logging.info(
            f"[UPLOAD] Signing with wallet hotkey: {wallet.hotkey.ss58_address[:8]}..."
        )
        timestamp = str(int(time.time()))
        signature = wallet.hotkey.sign(timestamp.encode())
        signature_b64 = base64.b64encode(signature).decode()
        bt.logging.info(f"[UPLOAD] Signature created, length: {len(signature_b64)}")

        # Prepare request
        url = "https://api.omron.ai/ptn/upload-proof"
        headers = {
            "x-signature": signature_b64,
            "x-timestamp": timestamp,
            "x-origin-ss58": wallet.hotkey.ss58_address,
            "Content-Type": "application/json",
        }

        payload = {
            "testnet": testnet,
            "proof": proof_hex,
            "public_signals": public_inputs_hex,
        }

        bt.logging.info(
            f"[UPLOAD] Payload sizes - proof: {len(proof_hex)}, public_signals: {len(public_inputs_hex)}"
        )
        bt.logging.info(
            f"[UPLOAD] Uploading proof for {wallet.hotkey.ss58_address[:8]} to {url}..."
        )

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        bt.logging.info(f"[UPLOAD] Response status code: {response.status_code}")

        if response.status_code == 200:
            bt.logging.success("✅ [UPLOAD] Proof uploaded successfully!")
            result = response.json()
            bt.logging.info(f"[UPLOAD] Response data: {result}")
            return result
        else:
            bt.logging.error(
                f"❌ [UPLOAD] Proof upload failed: {response.status_code} - {response.text}"
            )
            return None

    except requests.exceptions.Timeout as e:
        bt.logging.error(f"[UPLOAD] Timeout error uploading proof: {str(e)}")
        return None
    except requests.exceptions.ConnectionError as e:
        bt.logging.error(f"[UPLOAD] Connection error uploading proof: {str(e)}")
        return None
    except Exception as e:
        bt.logging.error(
            f"[UPLOAD] Unexpected error uploading proof: {type(e).__name__}: {str(e)}"
        )
        import traceback

        bt.logging.error(f"[UPLOAD] Traceback: {traceback.format_exc()}")
        return None


def save_zk_results(results, miner_hotkey):
    """
    Save ZK proof results to disk in ~/.pop/ directory.

    Args:
        results: The ZK results dictionary to save
        miner_hotkey: The miner's hotkey for filename
    """
    try:
        pop_dir = Path.home() / ".pop"
        pop_dir.mkdir(exist_ok=True)

        timestamp = int(time.time())
        filename = f"{miner_hotkey}_{timestamp}.json"
        filepath = pop_dir / filename

        with open(filepath, "w") as f:
            json.dump(results, f, indent=2, default=str)

        bt.logging.info(f"ZK results saved to {filepath}")
        return str(filepath)

    except Exception as e:
        bt.logging.error(f"Error saving ZK results: {str(e)}")
        return None


def get_latest_merkle_root_for_miner(hotkey):
    """
    Get the latest merkle root for a specific miner.

    Args:
        hotkey: The miner's hotkey

    Returns:
        dict with signals and returns merkle roots, or None if not found
    """
    try:
        pop_dir = Path.home() / ".pop"
        if not pop_dir.exists():
            return None

        matching_files = list(pop_dir.glob(f"{hotkey}_*.json"))
        if not matching_files:
            return None

        latest_file = max(matching_files, key=lambda f: f.stat().st_mtime)

        with open(latest_file, "r") as f:
            results = json.load(f)

        return results.get("merkle_roots")

    except Exception as e:
        bt.logging.error(f"Error getting latest merkle root for {hotkey}: {str(e)}")
        return None


def get_all_results_for_miner(hotkey):
    """
    Get all ZK results for a specific miner.

    Args:
        hotkey: The miner's hotkey

    Returns:
        list of result dictionaries sorted by timestamp (newest first)
    """
    try:
        pop_dir = Path.home() / ".pop"
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
                bt.logging.warning(f"Error reading {file_path}: {str(e)}")
                continue

        return sorted(results, key=lambda x: x["_timestamp"], reverse=True)

    except Exception as e:
        bt.logging.error(f"Error getting all results for {hotkey}: {str(e)}")
        return []


def generate_bb_proof(circuit_dir):
    bt.logging.info(f"Starting generate_bb_proof with circuit_dir: {circuit_dir}")

    try:
        version_result = subprocess.run(
            [BB_PATH, "--version"],
            capture_output=True,
            check=True,
            text=True,
        )
        bt.logging.info(f"bb version check passed: {version_result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        bt.logging.error(f"bb (Barretenberg) not found or failed version check: {e}")
        bt.logging.error(
            "Install with: curl -L https://raw.githubusercontent.com/AztecProtocol/aztec-packages/master/barretenberg/cpp/installation/install | bash"
        )
        return None, False

    target_dir = os.path.join(circuit_dir, "target")
    proof_dir = os.path.join(circuit_dir, "proof")
    bt.logging.info(f"Creating proof directory: {proof_dir}")
    os.makedirs(proof_dir, exist_ok=True)

    witness_file = os.path.join(target_dir, "witness.gz")
    circuit_file = os.path.join(target_dir, "circuits.json")

    bt.logging.info("Checking required files:")
    bt.logging.info(
        f"  witness_file: {witness_file} (exists: {os.path.exists(witness_file)})"
    )
    bt.logging.info(
        f"  circuit_file: {circuit_file} (exists: {os.path.exists(circuit_file)})"
    )

    if not os.path.exists(witness_file):
        bt.logging.error(f"Witness file not found: {witness_file}")
        return None, False
    if not os.path.exists(circuit_file):
        bt.logging.error(f"Circuit file not found: {circuit_file}")
        return None, False

    prove_cmd = [
        BB_PATH,
        "prove",
        "-b",
        circuit_file,
        "-w",
        witness_file,
        "-o",
        proof_dir,
        "--zk",
    ]
    bt.logging.info(f"Running bb prove command: {' '.join(prove_cmd)}")
    bt.logging.info(f"Working directory: {circuit_dir}")
    print(f"DEBUG: About to run bb prove: {' '.join(prove_cmd)}")
    print(f"DEBUG: Working directory: {circuit_dir}")
    print(f"DEBUG: BB_PATH exists: {os.path.exists(BB_PATH)}")
    print(f"DEBUG: Circuit file exists: {os.path.exists(circuit_file)}")
    print(f"DEBUG: Witness file exists: {os.path.exists(witness_file)}")

    prove_start = time.time()
    prove_result = subprocess.run(
        prove_cmd,
        capture_output=True,
        text=True,
        cwd=circuit_dir,
    )
    prove_time = time.time() - prove_start

    print(f"DEBUG: bb prove completed with return code: {prove_result.returncode}")
    print(f"DEBUG: bb prove time: {prove_time:.3f}s")
    bt.logging.info(
        f"bb prove completed in {prove_time:.3f}s with return code: {prove_result.returncode}"
    )

    if prove_result.stdout:
        bt.logging.info(f"bb prove stdout: {prove_result.stdout}")
        print(f"DEBUG: bb prove stdout: {prove_result.stdout}")
    if prove_result.stderr:
        bt.logging.info(f"bb prove stderr: {prove_result.stderr}")
        print(f"DEBUG: bb prove stderr: {prove_result.stderr}")

    if prove_result.returncode != 0:
        bt.logging.error(f"bb prove failed with return code {prove_result.returncode}")
        bt.logging.error(f"stderr: {prove_result.stderr}")
        bt.logging.error(f"stdout: {prove_result.stdout}")
        return None, False

    bt.logging.success(
        f"Proof of portfolio generated successfully in {prove_time:.3f}s"
    )

    proof_file = os.path.join(proof_dir, "proof")
    public_inputs_file = os.path.join(proof_dir, "public_inputs")
    bt.logging.info("Checking generated files:")
    bt.logging.info(
        f"  proof file: {proof_file} (exists: {os.path.exists(proof_file)})"
    )
    bt.logging.info(
        f"  public_inputs file: {public_inputs_file} (exists: {os.path.exists(public_inputs_file)})"
    )

    return prove_time, True


def generate_proof(
    data=None,
    daily_pnl=None,
    miner_hotkey=None,
    verbose=None,
    vali_config=None,
    use_weighting=False,
    bypass_confidence=False,
    daily_checkpoints=2,
    witness_only=False,
    account_size=None,
    wallet=None,
    testnet=True,
    augmented_scores=None,
):
    is_demo_mode = data is None
    if verbose is None:
        verbose = is_demo_mode

    logger = None
    log_file = None
    if miner_hotkey:
        logger, log_file = setup_proof_logging(miner_hotkey)
        logger.info(f"Starting proof generation for miner {miner_hotkey[:8]}...")
        print(f"Generating proof for {miner_hotkey[:8]}... (logs: {log_file})")

    def log(level, message):
        log_verbose(verbose, level, message, logger)

    if vali_config:
        days_in_year_crypto = vali_config.DAYS_IN_YEAR_CRYPTO
        weighted_average_decay_max = vali_config.WEIGHTED_AVERAGE_DECAY_MAX
        weighted_average_decay_min = vali_config.WEIGHTED_AVERAGE_DECAY_MIN
        weighted_average_decay_rate = vali_config.WEIGHTED_AVERAGE_DECAY_RATE
        omega_loss_minimum = vali_config.OMEGA_LOSS_MINIMUM
        sharpe_stddev_minimum = vali_config.SHARPE_STDDEV_MINIMUM
        sortino_downside_minimum = vali_config.SORTINO_DOWNSIDE_MINIMUM
        statistical_confidence_minimum_n_ceil = (
            vali_config.STATISTICAL_CONFIDENCE_MINIMUM_N_CEIL
        )
        annual_risk_free_decimal = vali_config.ANNUAL_RISK_FREE_DECIMAL
        omega_noconfidence_value = vali_config.OMEGA_NOCONFIDENCE_VALUE
        sharpe_noconfidence_value = vali_config.SHARPE_NOCONFIDENCE_VALUE
        sortino_noconfidence_value = vali_config.SORTINO_NOCONFIDENCE_VALUE
        calmar_noconfidence_value = vali_config.CALMAR_NOCONFIDENCE_VALUE
        statistical_confidence_noconfidence_value = (
            vali_config.STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE
        )
    else:
        days_in_year_crypto = 365
        weighted_average_decay_max = 1.0
        weighted_average_decay_min = 0.15
        weighted_average_decay_rate = 0.075
        omega_loss_minimum = 0.01
        sharpe_stddev_minimum = 0.01
        sortino_downside_minimum = 0.01
        statistical_confidence_minimum_n_ceil = 60
        annual_risk_free_decimal = 0.0419
        omega_noconfidence_value = 0.0
        sharpe_noconfidence_value = -100
        sortino_noconfidence_value = -100
        calmar_noconfidence_value = -100
        statistical_confidence_noconfidence_value = -100

    log(
        "info",
        f"generate_proof called with miner_hotkey={miner_hotkey[:8] if miner_hotkey else None}",
    )
    log(
        "info",
        f"Mode: {'Demo' if is_demo_mode else 'Production'}, verbose={verbose}",
    )
    try:
        if data is None:
            log("info", "Loading data from validator_checkpoint.json...")
            with open("validator_checkpoint.json", "r") as f:
                data = json.load(f)
    except Exception as e:
        bt.logging.error(f"Failed to load data {e}")

    if data is None:
        raise ValueError(
            "Failed to load data from validator_checkpoint.json in demo mode"
        )

    if miner_hotkey is None:
        miner_hotkey = list(data["perf_ledgers"].keys())[0]
        log(
            "info",
            f"No hotkey specified, using first available: {miner_hotkey}",
        )
    else:
        log("info", f"Using specified hotkey: {miner_hotkey}")

    if miner_hotkey not in data["perf_ledgers"]:
        raise ValueError(
            f"Hotkey '{miner_hotkey}' not found in data. Available: {list(data['perf_ledgers'].keys())}"
        )

    if daily_pnl is None:
        raise ValueError("daily_pnl must be provided")
    n_pnl = len(daily_pnl)
    scaled_daily_pnl = [scale_to_int(p) for p in daily_pnl]
    scaled_daily_pnl += [0] * (ARRAY_SIZE - n_pnl)
    positions = data["positions"][miner_hotkey]["positions"]
    log("info", "Preparing circuit inputs...")

    daily_log_returns = data.get("daily_returns", [])
    n_returns = len(daily_log_returns)

    if n_returns > MAX_DAYS:
        log(
            "warning",
            f"Truncating {n_returns} daily returns to {MAX_DAYS} (circuit limit)",
        )
        daily_log_returns = daily_log_returns[:MAX_DAYS]
        n_returns = MAX_DAYS

    scaled_log_returns = [int(ret * SCALE) for ret in daily_log_returns]

    scaled_log_returns += [0] * (MAX_DAYS - len(scaled_log_returns))

    checkpoint_returns = []
    checkpoint_mdds = []
    checkpoint_count = 0

    if "perf_ledgers" in data and miner_hotkey in data["perf_ledgers"]:
        ledger = data["perf_ledgers"][miner_hotkey]
        print(f"[PROOF_GEN] Ledger type: {type(ledger)}")

        if isinstance(ledger, list) and len(ledger) > 0:
            ledger = ledger[0]
            print(f"[PROOF_GEN] Using first ledger entry: {type(ledger)}")

        if hasattr(ledger, "cps") and ledger.cps:
            checkpoint_returns = [cp.gain + cp.loss for cp in ledger.cps]
            checkpoint_mdds = [cp.mdd for cp in ledger.cps]
            checkpoint_count = len(checkpoint_returns)
            log(
                "info",
                f"Extracted {checkpoint_count} checkpoint returns and MDDs",
            )
        elif isinstance(ledger, dict) and "cps" in ledger:
            checkpoint_returns = [cp["gain"] + cp["loss"] for cp in ledger["cps"]]
            checkpoint_mdds = [cp["mdd"] for cp in ledger["cps"]]
            checkpoint_count = len(checkpoint_returns)
            log(
                "info",
                f"Extracted {checkpoint_count} checkpoint returns and MDDs (dict format)",
            )

    MAX_CHECKPOINTS = 512
    if checkpoint_count > MAX_CHECKPOINTS:
        log(
            "warning",
            f"Truncating {checkpoint_count} checkpoint returns to {MAX_CHECKPOINTS} (circuit limit)",
        )
        checkpoint_returns = checkpoint_returns[:MAX_CHECKPOINTS]
        checkpoint_mdds = checkpoint_mdds[:MAX_CHECKPOINTS]
        checkpoint_count = MAX_CHECKPOINTS

    scaled_checkpoint_returns = [int(ret * SCALE) for ret in checkpoint_returns]
    scaled_checkpoint_mdds = [int(mdd * SCALE) for mdd in checkpoint_mdds]

    scaled_checkpoint_returns += [0] * (
        MAX_CHECKPOINTS - len(scaled_checkpoint_returns)
    )
    scaled_checkpoint_mdds += [SCALE] * (  # Default to 1.0 (no drawdown)
        MAX_CHECKPOINTS - len(scaled_checkpoint_mdds)
    )

    def extract_metric_value(scores_dict, metric_name):
        metric_data = scores_dict.get(metric_name, 0)
        if isinstance(metric_data, dict):
            return metric_data.get("value", 0)
        return metric_data

    python_calmar = extract_metric_value(augmented_scores, "calmar")
    python_sharpe = extract_metric_value(augmented_scores, "sharpe")
    python_sortino = extract_metric_value(augmented_scores, "sortino")
    python_omega = extract_metric_value(augmented_scores, "omega")

    avg_daily_pnl = sum(daily_pnl) / len(daily_pnl) if daily_pnl else 0
    base_return_percentage = avg_daily_pnl * 365 * 100
    if base_return_percentage != 0:
        risk_norm_factor = python_calmar / base_return_percentage
    else:
        risk_norm_factor = 0

    scaled_risk_norm_factor = int(risk_norm_factor * SCALE)

    weights_float = data.get("weights", [])

    scaled_weights = [int(w * SCALE) for w in weights_float]
    scaled_weights += [0] * (256 - len(scaled_weights))

    log("info", f"Using {n_returns} daily returns")
    try:
        all_orders = []
        for pos in positions:
            all_orders.extend(get_attr(pos, "orders"))

        signals_count = len(all_orders)
        if signals_count > MAX_SIGNALS:
            log(
                "warning",
                f"Truncating {signals_count} signals to {MAX_SIGNALS} (circuit limit)",
            )
            all_orders = all_orders[:MAX_SIGNALS]
            signals_count = MAX_SIGNALS

        trade_pair_map = {}
        trade_pair_counter = 0

        signals = []
        for order in all_orders:
            trade_pair = get_attr(order, "trade_pair")
            trade_pair_str = (
                str(trade_pair).split(".")[1]
                if hasattr(trade_pair, "name")
                else str(trade_pair)
            )
            if trade_pair_str not in trade_pair_map:
                trade_pair_map[trade_pair_str] = trade_pair_counter
                trade_pair_counter += 1

            order_type = get_attr(order, "order_type")
            if hasattr(order_type, "name"):
                order_type_parts = str(order_type).split(".")
                order_type_str = (
                    order_type_parts[1]
                    if len(order_type_parts) > 1
                    else order_type_parts[0]
                )
            else:
                order_type_str = str(order_type)
            order_type_map = {"SHORT": 2, "LONG": 1, "FLAT": 0}
            price = int(get_attr(order, "price") * SCALE)
            order_uuid = get_attr(order, "order_uuid")
            bid = int(get_attr(order, "bid") * SCALE)
            ask = int(get_attr(order, "ask") * SCALE)
            processed_ms = get_attr(order, "processed_ms")

            signals.append(
                {
                    "trade_pair": str(trade_pair_map[trade_pair_str]),
                    "order_type": str(order_type_map.get(order_type_str, 0)),
                    "leverage": str(int(abs(get_attr(order, "leverage")) * SCALE)),
                    "price": str(price),
                    "processed_ms": str(processed_ms),
                    "order_uuid": f"0x{str(order_uuid).replace('-', '')}",
                    "bid": str(bid),
                    "ask": str(ask),
                }
            )
    except Exception:
        traceback.print_exc()

    # Pad signals too
    signals += [
        {
            "trade_pair": "0",
            "order_type": "0",
            "leverage": "0",
            "price": "0",
            "processed_ms": "0",
            "order_uuid": "0x0",
            "bid": "0",
            "ask": "0",
        }
    ] * (MAX_SIGNALS - len(signals))

    log(
        "info",
        f"Prepared {n_returns} daily returns and {signals_count} signals for circuit",
    )

    if verbose:
        bt.logging.info(f"Circuit daily returns count: {n_returns}")
        bt.logging.info("Sample daily returns:")
        for i in range(min(5, n_returns)):
            bt.logging.info(
                f"  [{i}] return={daily_log_returns[i]:.6f} (scaled={scaled_log_returns[i]})"
            )
        if daily_log_returns:
            mean_return = sum(daily_log_returns) / len(daily_log_returns)
            bt.logging.info(f"Mean daily return: {mean_return:.6f}, count={n_returns}")

        bt.logging.info(f"Circuit checkpoint returns count: {checkpoint_count}")
        if checkpoint_count > 0:
            bt.logging.info("Sample checkpoint returns:")
            for i in range(min(5, checkpoint_count)):
                bt.logging.info(
                    f"  [{i}] return={checkpoint_returns[i]:.6f} (scaled={scaled_checkpoint_returns[i]})"
                )
            if checkpoint_returns:
                mean_checkpoint_return = sum(checkpoint_returns) / len(
                    checkpoint_returns
                )
                bt.logging.info(
                    f"Mean checkpoint return: {mean_checkpoint_return:.6f}, count={checkpoint_count}"
                )
        else:
            bt.logging.info(
                "No checkpoint returns found - using daily returns for Calmar calculation"
            )

        bt.logging.info(
            f"Circuit Config: MAX_DAYS={MAX_DAYS}, MAX_CHECKPOINTS={MAX_CHECKPOINTS}, DAILY_CHECKPOINTS=2"
        )

    log("info", "Running tree_generator circuit...")
    bt.logging.info(f"Generating tree for hotkey {miner_hotkey[:8]}...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tree_generator_dir = os.path.join(current_dir, "tree_generator")

    tree_prover_input = {"signals": signals, "actual_len": str(signals_count)}
    os.makedirs(tree_generator_dir, exist_ok=True)
    with open(os.path.join(tree_generator_dir, "Prover.toml"), "w") as f:
        toml.dump(tree_prover_input, f)

    output = run_command(
        [NARGO_PATH, "execute", "--silence-warnings"],
        tree_generator_dir,
        logger,
    )

    tree = parse_circuit_output(output)
    try:
        path_elements = tree["path_elements"]
        path_indices = tree["path_indices"]
        signals_merkle_root = tree["root"]
    except Exception:
        raise RuntimeError(
            "Unexpected tree_generator output structure, expected MerkleTree dict with leaf_hashes, path_elements, path_indices, and root"
        )

    log("info", f"Generated signals Merkle root: {signals_merkle_root}")
    log("info", "Returns Merkle root will be calculated within circuit")
    log("info", f"Number of daily returns: {n_returns}")
    log("info", "Running main proof of portfolio circuit...")
    bt.logging.info(f"Generating witness for hotkey {miner_hotkey[:8]}...")
    main_circuit_dir = os.path.join(current_dir, "circuits")

    # Pass annual risk-free rate (to match ann_excess_return usage)
    annual_risk_free_decimal = annual_risk_free_decimal
    risk_free_rate_scaled = int(annual_risk_free_decimal * SCALE)
    daily_rf_scaled = int(
        math.log(1 + annual_risk_free_decimal) / days_in_year_crypto * SCALE
    )

    account_size = data.get("account_size", 250000)
    # Finally, LFG
    main_prover_input = {
        "hotkey": str(miner_hotkey),
        "log_returns": [str(r) for r in scaled_log_returns],
        "n_returns": str(n_returns),
        "checkpoint_returns": [str(r) for r in scaled_checkpoint_returns],
        "checkpoint_count": str(checkpoint_count),
        "checkpoint_mdds": [str(mdd) for mdd in scaled_checkpoint_mdds],
        "risk_norm_factor": str(scaled_risk_norm_factor),
        "daily_pnl": [str(p) for p in scaled_daily_pnl],
        "n_pnl": str(n_pnl),
        "signals": signals,
        "signals_count": str(signals_count),
        "path_elements": [
            [
                field_to_toml_value(
                    int(x, 16) if isinstance(x, str) and x.startswith("0x") else int(x)
                )
                for x in p
            ]
            for p in path_elements
        ],
        "path_indices": [
            [
                int(x, 16) if isinstance(x, str) and x.startswith("0x") else int(x)
                for x in p
            ]
            for p in path_indices
        ],
        "signals_merkle_root": (
            signals_merkle_root
            if isinstance(signals_merkle_root, str)
            else str(signals_merkle_root)
        ),
        "risk_free_rate": str(risk_free_rate_scaled),
        "daily_rf": str(daily_rf_scaled),
        "use_weighting": str(int(use_weighting)),
        "weights": [str(w) for w in scaled_weights],
        "bypass_confidence": str(int(bypass_confidence)),
        "account_size": str(account_size),
        "days_in_year": str(days_in_year_crypto),
        "weighted_decay_max": str(int(weighted_average_decay_max * SCALE)),
        "weighted_decay_min": str(int(weighted_average_decay_min * SCALE)),
        "weighted_decay_rate": str(int(weighted_average_decay_rate * SCALE)),
        "omega_loss_min": str(int(omega_loss_minimum * SCALE)),
        "sharpe_stddev_min": str(int(sharpe_stddev_minimum * SCALE)),
        "sortino_downside_min": str(int(sortino_downside_minimum * SCALE)),
        "stat_conf_min_n": str(statistical_confidence_minimum_n_ceil),
        "annual_risk_free": str(int(annual_risk_free_decimal * SCALE)),
        "omega_noconfidence": str(int(omega_noconfidence_value * SCALE)),
        "sharpe_noconfidence": str(int(sharpe_noconfidence_value * SCALE)),
        "sortino_noconfidence": str(int(sortino_noconfidence_value * SCALE)),
        "calmar_noconfidence": str(int(calmar_noconfidence_value * SCALE)),
        "stat_confidence_noconfidence": str(
            int(statistical_confidence_noconfidence_value * SCALE)
        ),
    }

    # Scale and add the python metrics to the prover input
    scaled_sharpe = int(python_sharpe * SCALE)
    scaled_calmar = int(python_calmar * SCALE)
    scaled_sortino = int(python_sortino * SCALE)
    scaled_omega = int(python_omega * SCALE)

    main_prover_input["python_sharpe"] = str(scaled_sharpe)
    main_prover_input["python_calmar"] = str(scaled_calmar)
    main_prover_input["python_sortino"] = str(scaled_sortino)
    main_prover_input["python_omega"] = str(scaled_omega)

    os.makedirs(main_circuit_dir, exist_ok=True)
    with open(os.path.join(main_circuit_dir, "Prover.toml"), "w") as f:
        toml.dump(main_prover_input, f)

    log("info", "Executing main circuit to generate witness...")
    witness_start = time.time()
    if verbose:
        print(
            "[PROOF_GEN] Running nargo execute without silencing warnings to see debug output"
        )
        nargo_cmd = [NARGO_PATH, "execute", "witness"]

        # Run with capture to see both stdout and stderr
        result = subprocess.run(
            nargo_cmd, capture_output=True, text=True, cwd=main_circuit_dir
        )
        if result.returncode != 0:
            bt.logging.error(f"Command failed: {' '.join(nargo_cmd)}")
            bt.logging.error(f"stdout: {result.stdout}")
            bt.logging.error(f"stderr: {result.stderr}")
            raise RuntimeError(
                f"Command {' '.join(nargo_cmd)} failed with exit code {result.returncode}"
            )

        if result.stdout:
            print("[NARGO STDOUT]")
            print(result.stdout)
        if result.stderr:
            print("[NARGO STDERR - Debug Output]")
            print(result.stderr)

        output = result.stdout
    else:
        output = run_command(
            [NARGO_PATH, "execute", "witness", "--silence-warnings"],
            main_circuit_dir,
            logger,
        )
    witness_time = time.time() - witness_start
    log("info", f"Witness generation completed in {witness_time:.3f}s")

    fields = parse_circuit_output(output)
    log("info", f"Circuit output: {output}")
    log("info", f"Parsed fields: {fields}")
    if len(fields) < 8:
        raise RuntimeError(
            f"Expected 8 output fields from main circuit, got {len(fields)}: {fields}"
        )

    avg_daily_pnl_raw = fields[0]
    sharpe_raw = fields[1]
    drawdown_raw = fields[2]
    calmar_raw = fields[3]
    omega_raw = fields[4]
    sortino_raw = fields[5]
    stat_confidence_raw = fields[6]
    returns_merkle_root_raw = fields[7]

    def field_to_signed_int(field_str):
        if isinstance(field_str, str) and field_str.startswith("0x"):
            val = int(field_str, 16)
        else:
            val = int(field_str)

        # Noir's i64 as u64 casting uses standard two's complement
        # Convert from u64 back to i64 using two's complement
        if val >= 2**63:  # If the high bit is set, it's negative
            return val - 2**64  # Convert from unsigned to signed
        else:
            return val  # Positive values unchanged

    avg_daily_pnl_value = field_to_signed_int(avg_daily_pnl_raw)
    sharpe_ratio_raw = field_to_signed_int(sharpe_raw)
    max_drawdown_raw = field_to_signed_int(drawdown_raw)
    calmar_ratio_raw = field_to_signed_int(calmar_raw)
    omega_ratio_raw = field_to_signed_int(omega_raw)
    sortino_ratio_raw = field_to_signed_int(sortino_raw)
    stat_confidence_raw = field_to_signed_int(stat_confidence_raw)

    # Process returns merkle root (it's a Field, not signed)
    if isinstance(returns_merkle_root_raw, str) and returns_merkle_root_raw.startswith(
        "0x"
    ):
        returns_merkle_root = returns_merkle_root_raw
    else:
        returns_merkle_root = f"0x{int(returns_merkle_root_raw):x}"

    avg_daily_pnl_scaled = scale_from_int(avg_daily_pnl_value)
    avg_daily_pnl_ptn_scaled = avg_daily_pnl_scaled * 365 * 100
    sharpe_ratio_scaled = scale_from_int(sharpe_ratio_raw)
    max_drawdown_scaled = scale_from_int(max_drawdown_raw)
    calmar_ratio_scaled = scale_from_int(calmar_ratio_raw)
    omega_ratio_scaled = scale_from_int(omega_ratio_raw) / 1000000
    sortino_ratio_scaled = scale_from_int(sortino_ratio_raw)
    stat_confidence_scaled = scale_from_int(stat_confidence_raw)

    if witness_only:
        prove_time, proving_success = None, True
        log_verbose(
            verbose,
            "info",
            "Skipping barretenberg proof generation (witness_only=True)",
        )
    else:
        bt.logging.info(
            f"Starting barretenberg proof generation for {miner_hotkey[:8]}..."
        )
        try:
            prove_time, proving_success = generate_bb_proof(main_circuit_dir)
            bt.logging.info(
                f"generate_bb_proof returned: prove_time={prove_time}, proving_success={proving_success}"
            )
            if prove_time is None:
                bt.logging.error(
                    "Barretenberg proof generation failed - prove_time is None"
                )
                prove_time, proving_success = None, False
            elif not proving_success:
                bt.logging.error(
                    "Barretenberg proof generation failed - proving_success is False"
                )
        except Exception as e:
            bt.logging.error(
                f"Exception during proof generation: {type(e).__name__}: {e}"
            )
            bt.logging.error(f"Full traceback: {traceback.format_exc()}")
            prove_time, proving_success = None, False

    # Always print key production info: hotkey and verification status
    bt.logging.info(f"Hotkey: {miner_hotkey}")
    bt.logging.info(f"Orders processed: {signals_count}")
    bt.logging.info(f"Signals Merkle Root: {signals_merkle_root}")
    bt.logging.info(f"Returns Merkle Root: {returns_merkle_root}")
    bt.logging.info(f"Average Daily PnL: {avg_daily_pnl_scaled:.9f}")
    bt.logging.info(f"Sharpe Ratio: {sharpe_ratio_scaled:.9f}")
    # Convert drawdown factor to percentage: drawdown% = (1 - factor) * 100
    drawdown_percentage = max_drawdown_scaled * 100
    bt.logging.info(
        f"Max Drawdown: {max_drawdown_scaled:.9f} ({drawdown_percentage:.6f}%)"
    )
    bt.logging.info(f"Calmar Ratio: {calmar_ratio_scaled:.9f}")
    bt.logging.info(f"Omega Ratio: {omega_ratio_scaled:.9f}")
    bt.logging.info(f"Sortino Ratio: {sortino_ratio_scaled:.9f}")
    bt.logging.info(f"Statistical Confidence: {stat_confidence_scaled:.9f}")

    if verbose:
        bt.logging.info("\n--- Proof Generation Complete ---")
        bt.logging.info("\n=== MERKLE ROOTS ===")
        bt.logging.info(f"Signals Merkle Root: {signals_merkle_root}")
        bt.logging.info(f"Returns Merkle Root: {returns_merkle_root}")

        bt.logging.info("\n=== DATA SUMMARY ===")
        bt.logging.info(f"Daily returns processed: {n_returns}")
        bt.logging.info(f"Trading signals processed: {signals_count}")
        bt.logging.info("PnL calculated from cumulative returns in circuit")

        bt.logging.info("\n=== PROOF GENERATION RESULTS ===")
        bt.logging.info(f"Witness generation time: {witness_time:.3f}s")
        if not witness_only:
            if prove_time is not None:
                bt.logging.info(f"Proof generation time: {prove_time:.3f}s")
            else:
                bt.logging.info("Unable to prove due to an error.")

        # Circuit vs Subnet Comparison Table (verbose only)
        if augmented_scores:
            bt.logging.info(
                f"\n=== Circuit vs Subnet Comparison for {miner_hotkey[:8] if miner_hotkey else 'unknown'} ==="
            )
            bt.logging.info("Metric           Circuit    Subnet     Diff")
            bt.logging.info("=" * 50)

            metric_keys = {
                "sharpe": sharpe_ratio_scaled,
                "calmar": calmar_ratio_scaled,
                "sortino": sortino_ratio_scaled,
                "omega": omega_ratio_scaled,
            }

            for metric, circuit_value in metric_keys.items():
                subnet_value = augmented_scores.get(metric, 0.0)
                # Handle case where subnet_value is a dictionary with 'value' field
                if isinstance(subnet_value, dict):
                    subnet_value = subnet_value.get("value", 0.0)
                diff = abs(circuit_value - subnet_value)
                bt.logging.info(
                    f"{metric:<15} {circuit_value:>10.6f} {subnet_value:>10.6f} {diff:>10.6f}"
                )

    # Read proof and public inputs files to return as hex strings
    proof_hex = None
    public_inputs_hex = None

    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_circuit_dir = os.path.join(current_dir, "circuits")

    if prove_time is not None or witness_only:
        proof_path = os.path.join(main_circuit_dir, "proof", "proof")
        public_inputs_path = os.path.join(main_circuit_dir, "proof", "public_inputs")

        try:
            if os.path.exists(proof_path):
                with open(proof_path, "rb") as f:
                    proof_hex = f.read().hex()

            if os.path.exists(public_inputs_path):
                with open(public_inputs_path, "rb") as f:
                    public_inputs_hex = f.read().hex()
        except Exception as e:
            bt.logging.error(f"Error reading proof files: {str(e)}")

    # Upload proof if wallet provided and proof generation was successful
    upload_result = None
    bt.logging.info(
        f"[MAIN] Pre-upload check: wallet={bool(wallet)}, proof_hex={bool(proof_hex)} (len={len(proof_hex) if proof_hex else 0}), public_inputs_hex={bool(public_inputs_hex)} (len={len(public_inputs_hex) if public_inputs_hex else 0}), witness_only={witness_only}"
    )

    if wallet and proof_hex and public_inputs_hex and not witness_only:
        bt.logging.info(
            f"[MAIN] All conditions met, calling upload_proof with testnet={testnet}"
        )
        upload_result = upload_proof(proof_hex, public_inputs_hex, wallet, testnet)
    else:
        bt.logging.warning("[MAIN] Skipping upload - conditions not met:")
        if not wallet:
            bt.logging.warning("[MAIN]   - wallet is None/False")
        if not proof_hex:
            bt.logging.warning("[MAIN]   - proof_hex is None/False")
        if not public_inputs_hex:
            bt.logging.warning("[MAIN]   - public_inputs_hex is None/False")
        if witness_only:
            bt.logging.warning("[MAIN]   - witness_only is True")

    bt.logging.info(f"[MAIN] Proof upload result: {upload_result}")

    # Build results dictionary
    results = {
        "merkle_roots": {
            "signals": signals_merkle_root,
            "returns": returns_merkle_root,
        },
        "portfolio_metrics": {
            "avg_daily_pnl_raw": avg_daily_pnl_value,
            "avg_daily_pnl_scaled": avg_daily_pnl_scaled,
            "avg_daily_pnl_ptn_scaled": avg_daily_pnl_ptn_scaled,
            "sharpe_ratio_raw": sharpe_ratio_raw,
            "sharpe_ratio_scaled": sharpe_ratio_scaled,
            "max_drawdown_raw": max_drawdown_raw,
            "max_drawdown_scaled": max_drawdown_scaled,
            "max_drawdown_percentage": max_drawdown_scaled * 100,
            "calmar_ratio_raw": calmar_ratio_raw,
            "calmar_ratio_scaled": calmar_ratio_scaled,
            "omega_ratio_raw": omega_ratio_raw,
            "omega_ratio_scaled": omega_ratio_scaled,
            "sortino_ratio_raw": sortino_ratio_raw,
            "sortino_ratio_scaled": sortino_ratio_scaled,
            "stat_confidence_raw": stat_confidence_raw,
            "stat_confidence_scaled": stat_confidence_scaled,
        },
        "data_summary": {
            "daily_returns_processed": n_returns,
            "signals_processed": signals_count,
            "returns_processed": n_returns,
        },
        "circuit_inputs": {
            "daily_log_returns": daily_log_returns,
            "weights_float": weights_float,
            "scaled_weights": scaled_weights,
            "scaled_daily_pnl": scaled_daily_pnl,
            "scaled_daily_returns": scaled_log_returns,
            "scaled_checkpoint_returns": scaled_checkpoint_returns,
            "scaled_checkpoint_mdds": scaled_checkpoint_mdds,
            "risk_norm_factor": risk_norm_factor,
            "scaled_risk_norm_factor": scaled_risk_norm_factor,
            "n_returns": n_returns,
            "n_pnl": n_pnl,
            "checkpoint_count": checkpoint_count,
            "signals_count": signals_count,
            "sum_of_weights": (
                sum(weights_float)
                if weights_float is not None and len(weights_float) > 0
                else 0
            ),
            "weights_count": (
                len(weights_float)
                if weights_float is not None and len(weights_float) > 0
                else 0
            ),
        },
        "proof_results": {
            "witness_generation_time": witness_time,
            "proof_generation_time": prove_time,
            "proving_success": proving_success,
            "proof_generated": prove_time is not None or witness_only,
            "proof_hex": proof_hex,
            "public_inputs_hex": public_inputs_hex,
            "upload_result": upload_result,
        },
    }

    save_hotkey = miner_hotkey if miner_hotkey else "none"
    try:
        save_zk_results(results, save_hotkey)
    except Exception as e:
        bt.logging.error(f"Failed to save ZK results: {e}")

    if logger:
        logger.info("Proof generation completed successfully")
        logger.info(f"Signals Merkle Root: {signals_merkle_root}")
        logger.info(f"Returns Merkle Root: {returns_merkle_root}")
        print(
            f"Proof generated for {miner_hotkey[:8]} - Signals Root: {signals_merkle_root}"
        )

    return results
