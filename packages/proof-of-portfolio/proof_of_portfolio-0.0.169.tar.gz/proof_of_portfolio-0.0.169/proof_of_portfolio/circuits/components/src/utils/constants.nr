// Core array and data structure sizes
pub global ARRAY_SIZE: u32 = 256;
pub global MAX_DAYS: u32 = 256;
pub global MAX_RETURNS: u32 = 256;
pub global MAX_SIGNALS: u32 = 512;
pub global MAX_CHECKPOINTS: u32 = 512;

// Merkle tree configuration
pub global MERKLE_DEPTH: u32 = 8;

// Time and checkpoint constants
pub global DAILY_CHECKPOINTS: u32 = 2;
pub global SECONDS_PER_DAY: u64 = 86400;

pub global SCALE: i64 = 100_000_000; // SCALE: 10^8 for fixed-point precision

// Date and time constants
pub global DAYS_IN_YEAR: i64 = 365;
pub global STATISTICAL_CONFIDENCE_MINIMUM_N: u32 = 60;

// Risk-free rate (as basis points, 419 = 4.19%)
pub global ANNUAL_RISK_FREE_RATE_BP: i64 = 419;
pub global DAILY_LOG_RISK_FREE_RATE: i64 = 114794;

// Minimum values for ratio calculations (0.01 scaled by SCALE/100)
pub global SHARPE_STDDEV_MINIMUM: i64 = SCALE / 100;
pub global OMEGA_LOSS_MINIMUM: i64 = SCALE / 100;
pub global SORTINO_DOWNSIDE_MINIMUM: i64 = SCALE / 100;

// Scaling factors for precision in integer calculations
pub global OMEGA_SCALE_FACTOR: i64 = SCALE * 10;
pub global SHARPE_SCALE_FACTOR: i64 = SCALE / 100;
pub global LARGE_POSITIVE_VALUE: i64 = SCALE * 10;
// SCALE removed - use SCALE directly (10^8)

// Test values for no-confidence matching PTN defaults
pub global OMEGA_NOCONFIDENCE_VALUE: i64 = 0;
pub global SHARPE_NOCONFIDENCE_VALUE: i64 = -100 * SCALE;
pub global SORTINO_NOCONFIDENCE_VALUE: i64 = -100 * SCALE;
pub global CALMAR_NOCONFIDENCE_VALUE: i64 = -100 * SCALE;
pub global STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE: i64 = -100 * SCALE;

// Position and trading constants
pub global PRICE_SCALE: u64 = 1_000_000_000_000;
pub global LEVERAGE_SCALE: u32 = 10_000;

// Order type constants
pub global ORDER_TYPE_FLAT: u8 = 0;
pub global ORDER_TYPE_LONG: u8 = 1;
pub global ORDER_TYPE_SHORT: u8 = 2;

// Order source constants
pub global ORDER_SRC_ORGANIC: u8 = 1;

// Version timestamps for fee and slippage calculations
pub global FEE_V6_TIME_MS: u64 = 1720843707000;
pub global SLIPPAGE_V1_TIME_MS: u64 = 1739937600000;

// Drawdown thresholds for risk normalization (percentages)
pub global DRAWDOWN_MAXVALUE_PERCENTAGE: i64 = 10; // 10% max drawdown threshold
pub global DRAWDOWN_MINVALUE_PERCENTAGE: i64 = 1;  // 1% min drawdown threshold
