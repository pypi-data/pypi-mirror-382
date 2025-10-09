use crate::utils::{constants::{SCALE, SORTINO_DOWNSIDE_MINIMUM}, sqrt::sqrt};

pub fn sortino(
    actual_len: u32,
    bypass_confidence: bool,
    downside_variance_val: i64,
    ann_excess_return_val: i64,
    noconfidence_value: i64,
    minimum_n: u32,
    python_sortino: i64,
) -> i64 {
    if !bypass_confidence & actual_len < minimum_n {
        noconfidence_value
    } else {
        println(f"[SORTINO] downside_variance_val={downside_variance_val}");
        if downside_variance_val == 0 {
            let circuit_result: i64 = 0;

            let diff = if circuit_result > python_sortino {
                circuit_result - python_sortino
            } else {
                python_sortino - circuit_result
            };

            println(
                f"[SORTINO] No downside returns detected, circuit={circuit_result}, python={python_sortino}, diff={diff}",
            );
            println(
                f"[SORTINO] ERROR: Large diff detected! Expected circuit=0 to match python={python_sortino}",
            );

            let tolerance: i64 = 10000;
            assert(diff <= tolerance);

            python_sortino
        } else {
            let excess_return = ann_excess_return_val;

            let downside_volatility = if actual_len < 2 {
                SCALE
            } else {
                let scaled_annualized_downside_variance = (downside_variance_val as u64) * 365;

                let downside_vol_precise = sqrt(scaled_annualized_downside_variance);

                downside_vol_precise as i64
            };

            let effective_downside_volatility = if downside_volatility < SORTINO_DOWNSIDE_MINIMUM {
                SORTINO_DOWNSIDE_MINIMUM
            } else {
                downside_volatility
            };

            let result = (excess_return * SCALE) / effective_downside_volatility;

            let diff = if result > python_sortino {
                result - python_sortino
            } else {
                python_sortino - result
            };

            println(
                f"[SORTINO] Has downside: excess={excess_return}, downside_vol={effective_downside_volatility}, result={result}, python={python_sortino}, diff={diff}",
            );

            // Dynamic tolerance: 2% of the circuit calculated value
            let tolerance: i64 = (2 * result) / 100; // 0.02 * result
            assert(diff <= tolerance);

            python_sortino
        }
    }
}
