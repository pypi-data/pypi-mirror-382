use crate::utils::constants::{ARRAY_SIZE, SCALE};

pub fn omega(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    weights: [i64; ARRAY_SIZE],
    use_weighting: bool,
    bypass_confidence: bool,
    omega_loss_min: i64,
    noconfidence_value: i64,
    minimum_n: u32,
    python_omega: i64,
) -> i64 {
    if !bypass_confidence & actual_len < minimum_n {
        noconfidence_value
    } else {
        if use_weighting {
            let mut product_sum_positive: i64 = 0;
            let mut product_sum_negative: i64 = 0;
            let mut sum_weights_positive_raw: i64 = 0;
            let mut sum_weights_negative_raw: i64 = 0;

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    let weight = weights[i];
                    let log_return = log_returns[i];
                    if log_return > 0 {
                        product_sum_positive += (log_return * weight) / SCALE;
                        sum_weights_positive_raw += weight;
                    } else {
                        product_sum_negative += (log_return * weight) / SCALE;
                        sum_weights_negative_raw += weight;
                    }
                }
            }

            let sum_weights_positive = if sum_weights_positive_raw >= omega_loss_min {
                sum_weights_positive_raw
            } else {
                omega_loss_min
            };
            let sum_weights_negative = if sum_weights_negative_raw >= omega_loss_min {
                sum_weights_negative_raw
            } else {
                omega_loss_min
            };

            let positive_sum = (product_sum_positive * sum_weights_negative) / SCALE;
            let negative_sum = (product_sum_negative * sum_weights_positive) / SCALE;

            let numerator = positive_sum;
            let abs_negative_sum = if negative_sum >= 0 {
                negative_sum
            } else {
                -negative_sum
            };

            let effective_denominator = if abs_negative_sum >= omega_loss_min {
                abs_negative_sum
            } else {
                omega_loss_min
            };

            let result = if effective_denominator > 0 {
                (numerator * SCALE) / effective_denominator
            } else {
                0
            };

            let diff = if result > python_omega {
                result - python_omega
            } else {
                python_omega - result
            };

            println(
                f"[OMEGA-WEIGHTED] numerator={numerator}, eff_denom={effective_denominator}, result={result}, python={python_omega}, diff={diff}",
            );

            let tolerance: i64 = 500000;
            assert(diff <= tolerance);

            python_omega
        } else {
            let mut positive_sum: i64 = 0;
            let mut negative_sum: i64 = 0;
            let mut _count_pos: u32 = 0;
            let mut _count_neg: u32 = 0;

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    let log_return = log_returns[i];
                    if log_return > 0 {
                        positive_sum += log_return;
                    } else {
                        negative_sum += log_return;
                    }
                }
            }

            let effective_denominator = if -negative_sum >= omega_loss_min {
                -negative_sum
            } else {
                omega_loss_min
            };

            let result = (positive_sum * SCALE) / effective_denominator;

            let diff = if result > python_omega {
                result - python_omega
            } else {
                python_omega - result
            };

            println(
                f"[OMEGA] pos_sum={positive_sum}, neg_sum={negative_sum}, eff_denom={effective_denominator}, result={result}, python={python_omega}, diff={diff}",
            );

            let tolerance: i64 = 500000;
            assert(diff <= tolerance);

            python_omega
        }
    }
}
