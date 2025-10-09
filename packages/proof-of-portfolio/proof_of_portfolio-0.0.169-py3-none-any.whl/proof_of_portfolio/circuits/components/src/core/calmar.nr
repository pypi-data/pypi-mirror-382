use crate::utils::constants::{ARRAY_SIZE, SCALE};
use crate::utils::average::average;

pub fn calmar(
    returns_array: [i64; ARRAY_SIZE],
    n_returns: u32,
    weights: [i64; ARRAY_SIZE],
    use_weighting: bool,
    bypass_confidence: bool,
    days_in_year: i64,
    risk_norm_factor: i64,
    noconfidence_value: i64,
    minimum_n: u32,
    python_calmar: i64,
) -> i64 {
    if !bypass_confidence & n_returns < minimum_n {
        noconfidence_value
    } else {
        let sum_of_weights = if use_weighting {
            let mut sum: i64 = 0;
            for i in 0..ARRAY_SIZE {
                if (i as u32) < n_returns {
                    sum += weights[i];
                }
            }
            sum
        } else {
            n_returns as i64
        };

        let avg_daily_return = average(returns_array, n_returns, weights, use_weighting, sum_of_weights);

        let base_return_precise = avg_daily_return * days_in_year * 100;
        println(
            f"[CALMAR] Daily calc: avg_daily={avg_daily_return}, days_in_year={days_in_year}, base_return_precise={base_return_precise}",
        );

        let circuit_result = (base_return_precise * risk_norm_factor) / SCALE;

        let diff = if circuit_result > python_calmar {
            circuit_result - python_calmar
        } else {
            python_calmar - circuit_result
        };

        println(
            f"[CALMAR] avg_daily={avg_daily_return}, base_ret={base_return_precise}, risk_norm={risk_norm_factor}",
        );
        println(
            f"[CALMAR] circuit={circuit_result}, python={python_calmar}, diff={diff}",
        );
        println(
            f"[CALMAR] Calculation: ({base_return_precise} * {risk_norm_factor}) / {SCALE} = {circuit_result}",
        );

        let tolerance: i64 = 60000;
        assert(diff <= tolerance);

        python_calmar
    }
}
