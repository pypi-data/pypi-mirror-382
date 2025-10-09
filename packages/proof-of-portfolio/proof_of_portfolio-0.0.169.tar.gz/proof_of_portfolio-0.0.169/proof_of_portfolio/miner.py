import json
import os
import subprocess
import toml
import re
import logging
from pathlib import Path
from . import requires_dependencies


class Miner:
    def __init__(self, ss58_address, name):
        self.name = name
        self.ss58_address = ss58_address
        current_dir = os.path.dirname(os.path.abspath(__file__))

        package_tree_dir = os.path.join(current_dir, "tree_generator")
        dev_tree_dir = os.path.abspath(
            os.path.join(current_dir, "..", "tree_generator")
        )

        if os.path.exists(package_tree_dir):
            self.TREE_GEN_DIR = package_tree_dir
        elif os.path.exists(dev_tree_dir):
            self.TREE_GEN_DIR = dev_tree_dir
        else:
            raise FileNotFoundError(
                f"tree_generator directory not found. Tried: {package_tree_dir}, {dev_tree_dir}"
            )

        self.TREE_GEN_PROVER_TOML = os.path.join(self.TREE_GEN_DIR, "Prover.toml")
        self.MAX_SIGNALS = 512

        log_dir = Path.home() / ".pop"
        log_dir.mkdir(exist_ok=True)
        self.log_file = log_dir / f"{ss58_address[:16]}_log.log"

        self.logger = logging.getLogger(f"pop.{ss58_address[:8]}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        handler = logging.FileHandler(self.log_file)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(handler)

    def prepare_signals_from_data(self, data_json_path):
        """
        Reads the data.json file for a hotkey, extracts all their orders,
        and transforms them into a list of TradingSignal dicts for the circuits.

        Args:
            data_json_path (str): Path to the data.json file

        Returns:
            tuple: (padded_signals, actual_len)
        """
        self.logger.info(f"Preparing signals from {data_json_path}")
        try:
            with open(data_json_path, "r") as f:
                positions = json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Data file not found at {data_json_path}")
            return None, 0
        except json.JSONDecodeError:
            self.logger.error(f"Could not decode JSON from {data_json_path}")
            return None, 0

        if not positions:
            self.logger.warning(f"No positions found in {data_json_path}")
            return [], 0

        orders = []

        if isinstance(positions, dict):
            if "positions" in positions:
                position_list = positions["positions"]
            else:
                self.logger.warning(f"Unexpected data structure for {data_json_path}")
                return [], 0
        else:
            position_list = positions

        orders = []
        for position in position_list:
            orders.extend(position.get("orders", []))

        orders.sort(key=lambda o: o["processed_ms"])

        signals = []

        for i in range(0, len(orders), 2):
            if (i + 1) >= len(orders) or len(signals) >= self.MAX_SIGNALS:
                break

            open_order = orders[i]
            close_order = orders[i + 1]

            order_type_map = {"SHORT": 2, "LONG": 1, "FLAT": 0}
            order_type_code = order_type_map.get(open_order["order_type"], 0)

            open_uuid_hex = open_order["order_uuid"].replace("-", "")
            close_uuid_hex = close_order["order_uuid"].replace("-", "")

            signals.append(
                {
                    "trade_pair": "0",
                    "order_type": str(order_type_code),
                    "leverage": str(int(abs(open_order["leverage"]) * 100)),
                    "price": str(int(open_order["price"] * 100)),
                    "processed_ms": str(open_order["processed_ms"]),
                    "order_uuid": f"0x{open_uuid_hex}",
                    "bid": str(int(open_order.get("bid", 0) * 100)),
                    "ask": str(int(open_order.get("ask", 0) * 100)),
                }
            )

            signals.append(
                {
                    "trade_pair": "0",
                    "order_type": "0",
                    "leverage": str(int(abs(open_order["leverage"]) * 100)),
                    "price": str(int(close_order["price"] * 100)),
                    "processed_ms": str(close_order["processed_ms"]),
                    "order_uuid": f"0x{close_uuid_hex}",
                    "bid": str(int(close_order.get("bid", 0) * 100)),
                    "ask": str(int(close_order.get("ask", 0) * 100)),
                }
            )

        actual_len = len(signals)
        if actual_len == 0:
            print(f"Warning: No valid order pairs found in {data_json_path}")
            return [], 0

        padded_signals = signals + [
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
        ] * (self.MAX_SIGNALS - actual_len)

        self.logger.info(f"Successfully prepared {actual_len} signals")
        return padded_signals, actual_len

    def run_merkle_generator(self, signals, actual_len):
        """
        Runs the merkle_generator circuit and parses the witness file to get the output.

        Args:
            signals (list): List of trading signals
            actual_len (int): Actual number of signals

        Returns:
            tuple: (merkle_root, path_elements, path_indices) or None if failed
        """
        self.logger.info("Running Merkle Generator circuit")

        merkle_input = {"signals": signals, "actual_len": actual_len}

        witness_name = "merkle_witness"
        witness_path = os.path.join(self.TREE_GEN_DIR, "target", f"{witness_name}.gz")

        with open(self.TREE_GEN_PROVER_TOML, "w") as f:
            toml.dump(merkle_input, f)

        nargo_cmd = "nargo"

        nargo_paths = [
            os.path.expanduser("~/.nargo/bin/nargo"),
            os.path.expanduser("~/.noir/bin/nargo"),
            os.path.expanduser("~/.cargo/bin/nargo"),
            os.path.expanduser("~/.noirup/bin/nargo"),
        ]

        for path in nargo_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                nargo_cmd = path
                self.logger.info(f"Found nargo at: {nargo_cmd}")
                break

        self.logger.info("Executing nargo")
        result = subprocess.run(
            [nargo_cmd, "execute", witness_name, "--silence-warnings"],
            cwd=self.TREE_GEN_DIR,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            self.logger.error(f"Merkle generator execution failed: {result.stderr}")
            return None

        self.logger.info(
            f"Merkle generator executed successfully. Witness saved to {witness_path}"
        )

        try:
            output_str = result.stdout

            def parse_hex_root(text):
                match = re.search(r"root: (0x[0-9a-fA-F]+)", text)
                return str(int(match.group(1), 16)) if match else None

            def parse_nested_hex_array(text, start_marker, end_marker):
                start_idx = text.find(start_marker)
                if start_idx == -1:
                    return []

                start_idx += len(start_marker)
                end_idx = text.find(end_marker, start_idx)
                if end_idx == -1:
                    return []

                section = text[start_idx:end_idx]
                result = []
                depth = 0
                current_array = []
                current_hex = ""

                i = 0
                while i < len(section):
                    char = section[i]

                    if char == "[":
                        depth += 1
                        if depth == 2:
                            current_array = []
                    elif char == "]":
                        if current_hex:
                            current_array.append(str(int(current_hex, 16)))
                            current_hex = ""
                        depth -= 1
                        if depth == 1:
                            result.append(current_array)
                            current_array = []
                    elif char == "0" and i + 1 < len(section) and section[i + 1] == "x":
                        if current_hex:
                            current_array.append(str(int(current_hex, 16)))
                        current_hex = "0x"
                        i += 1
                    elif current_hex and (char.isdigit() or char in "abcdefABCDEF"):
                        current_hex += char
                    elif current_hex and char in ", ":
                        current_array.append(str(int(current_hex, 16)))
                        current_hex = ""

                    i += 1

                return result

            merkle_root = parse_hex_root(output_str)
            if not merkle_root:
                raise ValueError("Could not parse Merkle root from output")

            if "MerkleTree {" in output_str:
                path_elements = parse_nested_hex_array(
                    output_str, "path_elements: ", ", path_indices:"
                )
                path_indices = parse_nested_hex_array(
                    output_str, "path_indices: ", ", root:"
                )

                if path_elements and path_indices:
                    self.logger.info(
                        "Successfully parsed Merkle tree data from circuit output"
                    )
                    return merkle_root, path_elements, path_indices

            self.logger.warning(
                "Could not parse path_elements/path_indices, returning tree with root only"
            )
            return merkle_root, [], []

        except Exception as e:
            self.logger.error(f"Failed to parse Merkle generator output: {e}")
            return None

    @requires_dependencies
    def generate_tree(self, input_json_path: str, output_path: str = None):
        """
        Generates a Merkle tree from a child hotkey data.json file and saves it to the specified path.

        Args:
            input_json_path (str): Path to the child hotkey data.json file
            output_path (str, optional): Path where the tree.json file will be saved.
                                    If not provided, saves to the same directory as the input file.

        Returns:
            dict: Tree data containing merkle_root, path_elements, and path_indices, or None if failed
        """

        signals, actual_len = self.prepare_signals_from_data(input_json_path)
        if not signals or actual_len == 0:
            print("Could not prepare signals. Exiting.")
            return None

        merkle_data = self.run_merkle_generator(signals, actual_len)
        if not merkle_data:
            print("Halting due to error in Merkle generation.")
            return None

        merkle_root, path_elements, path_indices = merkle_data

        tree_data = {
            "merkle_root": merkle_root,
            "path_elements": path_elements,
            "path_indices": path_indices,
            "actual_len": actual_len,
        }

        if output_path:
            if os.path.isdir(output_path):
                tree_file = os.path.join(output_path, "tree.json")
            else:
                tree_file = output_path
        else:
            output_dir = os.path.dirname(input_json_path)
            tree_file = os.path.join(output_dir, "tree.json")

        try:
            os.makedirs(os.path.dirname(os.path.abspath(tree_file)), exist_ok=True)

            with open(tree_file, "w") as f:
                json.dump(tree_data, f, indent=2)
            print(f"Tree data saved to {tree_file}")
        except Exception as e:
            print(f"Error saving tree data: {e}")
            return None

        if os.path.exists(self.TREE_GEN_PROVER_TOML):
            os.remove(self.TREE_GEN_PROVER_TOML)

        merkle_witness_path = os.path.join(
            self.TREE_GEN_DIR, "target", "merkle_witness.gz"
        )
        if os.path.exists(merkle_witness_path):
            os.remove(merkle_witness_path)

        return tree_data

    def visualize_tree(self, tree_data):
        """
        Visualizes the merkle tree in a user-friendly format with ASCII art.
        Only shows the first "actual_len" path elements, ignoring filler paths.

        Args:
            tree_data (dict): Tree data containing merkle_root, path_elements, and path_indices

        Returns:
            str: A string representation of the tree with ASCII art
        """
        if not tree_data:
            return "No tree data available."

        merkle_root = tree_data["merkle_root"]
        path_elements = tree_data["path_elements"]
        path_indices = tree_data.get("path_indices", [])
        actual_len = tree_data.get("actual_len", 0)

        box_width = 70
        content_width = box_width - 2

        def shorten_hash(hash_str):
            hash_str = str(hash_str)
            if len(hash_str) <= 14:
                return hash_str
            return f"{hash_str[:6]}...{hash_str[-6:]}"

        tree_str = []
        title = f"🌳 Merkle Tree (Signals: {actual_len}) 🌳"
        tree_str.append(title)
        tree_str.append("═" * box_width)

        if isinstance(merkle_root, str):
            merkle_root_str = merkle_root
        else:
            merkle_root_str = str(merkle_root)
        short_root = shorten_hash(merkle_root_str)

        tree_str.append(f"Root: {short_root}")
        tree_str.append("╔" + "═" * (box_width - 2) + "╗")

        max_paths_to_show = min(actual_len, len(path_elements))

        for i in range(max_paths_to_show):
            elements = path_elements[i]
            indices = path_indices[i] if i < len(path_indices) else []

            path_header = f"║ Path {i + 1}:"
            if i == 0:
                tree_str.append(
                    path_header + " " * (content_width - len(path_header)) + "║"
                )
            else:
                tree_str.append("║" + "─" * (box_width - 2) + "║")
                tree_str.append(
                    path_header + " " * (content_width - len(path_header)) + "║"
                )

            for level, element in enumerate(elements):
                short_element = shorten_hash(element)

                direction = ""
                if level < len(indices):
                    direction = "→ Right" if indices[level] == "1" else "→ Left"

                max_visible_depth = 4
                if level == 0:
                    prefix = "║ ├── "
                elif level < max_visible_depth:
                    prefix = "║ │   " * level + "├── "
                else:
                    prefix = (
                        "║ │   " * (max_visible_depth - 1)
                        + "├─"
                        + "─" * (level - max_visible_depth + 1)
                        + " "
                    )

                node_info = f"Level {level + 1}: {short_element} {direction}"
                line = f"{prefix}{node_info}"

                if len(line) > box_width - 1:
                    available_space = box_width - 1 - len(prefix) - 3

                    truncated_node_info = node_info[:available_space] + "..."
                    line = f"{prefix}{truncated_node_info}"

                tree_str.append(line + " " * (box_width - 1 - len(line)) + "║")

        if len(path_elements) > max_paths_to_show:
            tree_str.append("║" + "─" * (box_width - 2) + "║")
            more_paths_msg = (
                f"║ ... {len(path_elements) - max_paths_to_show} more paths ..."
            )
            tree_str.append(
                more_paths_msg + " " * (box_width - 1 - len(more_paths_msg)) + "║"
            )

        tree_str.append("╚" + "═" * (box_width - 2) + "╝")

        return "\n".join(tree_str)

    def __str__(self):
        return self.name
