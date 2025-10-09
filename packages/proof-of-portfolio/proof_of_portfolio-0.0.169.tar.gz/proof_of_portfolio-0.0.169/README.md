# Proof of Portfolio

**A decentralized framework for verifiable, private performance metrics using Zero-Knowledge Proofs.**

[Explorer](https://ptn.omron.ai) | [Docs](https://inferencelabs.gitbook.io/proof-of-portfolio/) | [PyPI](https://pypi.org/project/proof-of-portfolio/) | [API](https://api.omron.ai/docs#tag/default/get/ptn/{validator_hotkey})

Proof of Portfolio (PoP) is a framework that enables **Validators** to generate verifiable attestations of private portfolio performance. The system provides tooling for the original data owners (**Miners**) and consumers (**Signal Purchasers**) to cryptographically verify these attestations—ensuring both data inclusion and correctness of calculated metrics—all without the validator ever exposing the underlying private data.

This is achieved by combining Merkle trees to commit to a history of portfolio data and [Noir](https://noir-lang.org/), a DSL for creating and verifying zero-knowledge proofs.

---

## Table of Contents

- [Proof of Portfolio](#proof-of-portfolio)
  - [Table of Contents](#table-of-contents)
  - [Core Concepts](#core-concepts)
  - [Project Structure](#project-structure)
  - [Installation](#installation)
    - [Automatically](#automatically)
    - [Manually](#manually)
      - [1. Prerequisites](#1-prerequisites)
      - [2. Standard Installation](#2-standard-installation)
      - [3. Installer Script (Optional)](#3-installer-script-optional)
  - [Usage Workflow](#usage-workflow)
    - [1. Validator: Generating Proofs](#1-validator-generating-proofs)
    - [2. Miner: Verifying Inclusion](#2-miner-verifying-inclusion)
    - [Utility Commands](#utility-commands)
  - [Demos](#demos)
  - [Development](#development)

---

## Core Concepts

The PoP system establishes trust through a validator-centric attestation model. It assumes a validator already has access to a set of private miner data. The tooling then facilitates a cryptographic process built on two key principles:

1.  **Merkle Trees**: A validator takes a miner's private portfolio history (checkpoints, positions, orders) and builds a Merkle tree from it. The resulting **Merkle Root** is made public. This root acts as a secure, tamper-proof fingerprint of the miner's entire dataset.

2.  **Zero-Knowledge Proofs (ZKPs)**: Using circuits written in Noir, the validator generates a proof that specific performance metrics were calculated correctly over the private data corresponding to the public Merkle root.

This combination allows for **verifiable, private computation**. Miners and signal purchasers can trust the publicly-stated performance metrics because:

- They can cryptographically verify their data was included in the calculation (by comparing their own data's Merkle root to the one the validator published).
- They can cryptographically verify the calculation itself was performed correctly (via the ZK proof).

The miner's sensitive financial data remains confidential throughout the entire process.

---

## Project Structure

The repository is organized into two main directories:

- `circuits/`: Contains all the Noir source code. The core logic for financial calculations (Sharpe ratio, returns, etc.) and the main circuit for verifying a miner's data against their Merkle root are defined here.
- `src/`: Contains the Python source code for the CLI, miner and validator logic, and demonstration scripts.

---

## Installation

The project is managed with Python and requires the `nargo` toolchain for interacting with Noir circuits.

### Automatically

```bash
uv add proof-of-portfolio
```

or

```bash
pip install proof-of-portfolio
```

> [!NOTE]
> When you run `pop` via the command line or import the package for the first time, it will automatically attempt to install the required barretenburg (bbup) and noir (nargo / noirup) dependencies

### Manually

#### 1. Prerequisites

Ensure you have [Noir/Nargo](https://noir-lang.org/docs/getting_started/installation) installed.

#### 2. Standard Installation

Clone the repository and install the package in editable mode. This will install the `pop` command-line tool and all necessary Python dependencies.

```bash
git clone https://github.com/inference-labs-inc/proof-of-portfolio.git
cd proof-of-portfolio
pip install -e .
```

#### 3. Installer Script (Optional)

An `install.sh` script is provided for convenience, which can help automate dependency setup.

```bash
./install.sh
```

---

## Usage Workflow

The `pop` command-line interface provides tools for all participants in the ecosystem. The primary workflow is validator-driven.

### 1. Validator: Generating Proofs

Validators use the PoP toolkit to attest to the performance of miner data they possess.

First, a validator might use `analyse-data` to split a large file of all miner data into a standardized directory structure.

```bash
pop analyse-data --path validator_checkpoint.json --output ./miner_data/
```

Next, the validator processes each miner's data to generate a score and a Merkle root.

```bash
# Process a single miner's data
pop validate --path ./miner_data/5H.../data.json

# Process all miners in a directory
pop validate-all --path ./miner_data/
```

This produces a `score.json` file for each miner, containing the calculated metrics and the public Merkle root that commits to the data used.

### 2. Miner: Verifying Inclusion

After a validator publishes a Merkle root, a miner can independently verify that their data was included and processed correctly without tampering.

The miner runs the `generate-tree` command on their own private data.

```bash
# Miner provides the path to their own data file
pop generate-tree --path ./path/to/my_private_data.json
```

This command outputs a Merkle root. The miner can then compare this root to the one published by the validator. If they match, the miner has cryptographic proof that the validator used their exact data.

### Utility Commands

- **`generate-test-data`**: Creates a randomized `validator_checkpoint.json`-style file for testing.
  ```bash
  pop generate-test-data --num-miners 5 --output-file test_data.json
  ```
- **`save-tree`**: A helper utility to save a `tree.json` file to a different location.

---

## Demos

The CLI includes a demo mode for testing purposes.

```bash
pop demo --help
```

- **`main`**: Runs a comprehensive end-to-end test, including ZKP generation and verification with Barretenberg.

**Example:**

```bash
pop demo main --hotkey 5H...
```

---

## Development

The project is under active development. Contributions are welcome. Please refer to the source code and circuits for detailed implementation information.
