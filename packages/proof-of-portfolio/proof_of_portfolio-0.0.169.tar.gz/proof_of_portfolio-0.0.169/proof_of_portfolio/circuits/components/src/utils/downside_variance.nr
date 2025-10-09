use crate::utils::{average::average, constants::ARRAY_SIZE};

pub fn downside_variance(
    daily_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    ddof: u32,
    weights: [i64; ARRAY_SIZE],
    use_weighting: bool,
    daily_rf: i64,
) -> i64 {
    let mut downside_variance = 0;

    let sum_of_weights = if use_weighting {
        let mut sum: i64 = 0;
        for i in 0..ARRAY_SIZE {
            if (i as u32) < actual_len {
                sum += weights[i];
            }
        }
        sum
    } else {
        actual_len as i64
    };

    let mean = average(
        daily_returns,
        actual_len,
        weights,
        use_weighting,
        sum_of_weights,
    );

    println(f"[DOWNSIDE_VAR] Using daily_rf={daily_rf} not mean={mean}");

    let mut downside_indices: [u32; ARRAY_SIZE] = [0; ARRAY_SIZE];
    let mut downside_count: u32 = 0;

    for i in 0..ARRAY_SIZE {
        if (i as u32) < actual_len {
            let return_val = daily_returns[i];
            if return_val < daily_rf {
                downside_indices[downside_count] = i as u32;
                downside_count += 1;
                println(
                    f"[DOWNSIDE_VAR] Downside return {downside_count}: {return_val} at index {i}",
                );
            } else {
                println(
                    f"[DOWNSIDE_VAR] i={i}, return={return_val} >= daily_rf={daily_rf}, skipping",
                );
            }
        }
    }

    let mut sum_sq_diff: u128 = 0;
    if downside_count > 0 {
        let downside_mean = if use_weighting {
            let mut weighted_sum: i64 = 0;
            let mut downside_weight_sum: i64 = 0;

            for i in 0..ARRAY_SIZE {
                if i < downside_count {
                    let idx = downside_indices[i];
                    let return_val = daily_returns[idx];
                    let weight_val = weights[idx];
                    weighted_sum += (return_val * weight_val) / 100000000; // SCALE
                    downside_weight_sum += weight_val;
                }
            }

            if downside_weight_sum > 0 {
                weighted_sum / (downside_weight_sum / 100000000)
            } else {
                0
            }
        } else {
            let mut sum: i64 = 0;
            for i in 0..ARRAY_SIZE {
                if i < downside_count {
                    let idx = downside_indices[i];
                    sum += daily_returns[idx];
                }
            }
            sum / (downside_count as i64)
        };

        println(
            f"[DOWNSIDE_VAR] Downside count: {downside_count}, mean: {downside_mean}",
        );

        for i in 0..ARRAY_SIZE {
            if i < downside_count {
                let idx = downside_indices[i];
                let return_val = daily_returns[idx];
                let diff_from_downside_mean = return_val - downside_mean;

                if use_weighting {
                    // Apply the same u128 approach as in variance calculation
                    let abs_diff: u128 = if diff_from_downside_mean < 0 {
                        (-diff_from_downside_mean) as u128
                    } else {
                        diff_from_downside_mean as u128
                    };
                    let sq_diff: u128 = abs_diff * abs_diff;
                    let weight_u128: u128 = weights[idx] as u128;
                    let scale_u128: u128 = 100000000; // SCALE
                    let contrib = (sq_diff * weight_u128) / scale_u128;
                    sum_sq_diff += contrib;
                } else {
                    let sq_diff = diff_from_downside_mean * diff_from_downside_mean;
                    sum_sq_diff += sq_diff as u128;
                }

                println(
                    f"[DOWNSIDE_VAR] Downside {i}: idx={idx}, return={return_val}, diff={diff_from_downside_mean}",
                );
            }
        }
    }

    if use_weighting {
        // Calculate the sum of weights for downside indices
        let mut downside_weight_sum: i64 = 0;
        for i in 0..ARRAY_SIZE {
            if i < downside_count {
                let idx = downside_indices[i];
                downside_weight_sum += weights[idx];
            }
        }

        if downside_weight_sum > 0 {
            let scale = 100000000; // SCALE constant
            let scaled_numerator = sum_sq_diff * (scale as u128);
            downside_variance = (scaled_numerator / (downside_weight_sum as u128)) as i64;
        }

        println(
            f"[DOWNSIDE_VAR] Final: sum_sq_diff={sum_sq_diff}, denominator={downside_weight_sum}, result={downside_variance}",
        );
    } else {
        if downside_count > 0 {
            downside_variance = (sum_sq_diff / (downside_count as u128)) as i64;
        }

        println(
            f"[DOWNSIDE_VAR] Final: sum_sq_diff={sum_sq_diff}, denominator={downside_count}, result={downside_variance}",
        );
    }

    downside_variance
}
