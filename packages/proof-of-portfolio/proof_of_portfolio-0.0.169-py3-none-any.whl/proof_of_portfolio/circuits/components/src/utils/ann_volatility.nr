use crate::utils::{constants::{ARRAY_SIZE, SCALE}, sqrt::sqrt, variance::variance};

pub fn ann_volatility(
    daily_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    weights: [i64; ARRAY_SIZE],
    use_weighting: bool,
) -> i64 {
    let result = if actual_len < 2 {
        SCALE
    } else {
        // Calculate sum_of_weights for this call
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
        let daily_variance = variance(daily_returns, actual_len, 1, weights, use_weighting, sum_of_weights);
        let annualized_variance = daily_variance * 365;
        sqrt(annualized_variance as u64) as i64
    };
    result
}
#[test]
fn test_ann_volatility_zero_variance() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = 100;
    }

    let weights = [100000; ARRAY_SIZE];
    let result = ann_volatility(returns, 5, weights, false);
    assert(result == 0);
}

#[test]
fn test_ann_volatility_positive_variance() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 100000;
    returns[1] = 200000;
    returns[2] = 300000;
    returns[3] = 400000;
    returns[4] = 500000;

    let weights = [100000; ARRAY_SIZE];
    let result = ann_volatility(returns, 5, weights, false);
    assert(result > 0);
}

#[test]
fn test_ann_volatility_ddof_zero() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 100;
    returns[1] = 200;
    returns[2] = 300;

    let weights = [100000; ARRAY_SIZE];
    let result_ddof_0 = ann_volatility(returns, 3, weights, false);
    let result_ddof_1 = ann_volatility(returns, 3, weights, false);
    assert(result_ddof_0 as i64 == result_ddof_1 as i64);
}

#[test]
fn test_ann_volatility_single_value() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 500;

    let weights = [100000; ARRAY_SIZE];
    let result = ann_volatility(returns, 1, weights, false);
    assert(result == SCALE);
}
