use crate::utils::constants::ARRAY_SIZE;

pub fn average(
    daily_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    weights: [i64; ARRAY_SIZE],
    use_weighting: bool,
    sum_of_weights: i64,
) -> i64 {
    let mut result = 0;
    if actual_len > 0 {
        if use_weighting {
            let mut weighted_sum: i64 = 0;

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    weighted_sum += daily_returns[i] * weights[i];
                }
            }
            if sum_of_weights != 0 {
                result = weighted_sum / sum_of_weights;
                println(
                    f"[AVERAGE] weighted: weighted_sum={weighted_sum}, sum_of_weights={sum_of_weights}, result={result}",
                );
            } else {
                println(f"[AVERAGE] weighted: sum_of_weights=0, returning 0");
            }
        } else {
            let mut sum: i64 = 0;
            println(
                f"[AVERAGE] unweighted calculation starting, actual_len={actual_len}",
            );
            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    let return_val = daily_returns[i];
                    println(f"[AVERAGE] i={i}, return_val={return_val}");
                    sum += return_val;
                    println(f"[AVERAGE] sum now={sum}");
                }
            }
            let denominator = actual_len as i64;
            println(f"[AVERAGE] Final: sum={sum}, denominator={denominator}");
            result = sum / denominator;
            println(
                f"[AVERAGE] unweighted: sum={sum}, actual_len={actual_len}, result={result}",
            );
        }
    } else {
        println(f"[AVERAGE] actual_len=0, returning 0");
    }
    result
}

#[test]
fn test_average_positive_numbers() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 100;
    returns[1] = 200;
    returns[2] = 300;

    let weights = [100000; ARRAY_SIZE];
    let result = average(returns, 3, weights, false, 3);
    assert(result == 200);
}

#[test]
fn test_average_negative_numbers() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = -100;
    returns[1] = -200;
    returns[2] = -300;

    let weights = [100000; ARRAY_SIZE];
    let result = average(returns, 3, weights, false, 3);
    assert(result == -200);
}

#[test]
fn test_average_mixed_numbers() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 100;
    returns[1] = -200;
    returns[2] = 300;
    returns[3] = -400;

    let weights = [100000; ARRAY_SIZE];
    let result = average(returns, 4, weights, false, 4);
    assert(result == -50);
}

#[test]
fn test_average_single_number() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 500;

    let weights = [100000; ARRAY_SIZE];
    let result = average(returns, 1, weights, false, 1);
    assert(result == 500);
}

#[test]
fn test_average_zeros() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..10 {
        returns[i] = 0;
    }

    let weights = [100000; ARRAY_SIZE];
    let result = average(returns, 10, weights, false, 10);
    assert(result == 0);
}
