use crate::utils::constants::{ARRAY_SIZE, SCALE};

pub fn exp_scaled(x_scaled: i64) -> i64 {
    let scale: i64 = SCALE;
    let mut abs_x = x_scaled;
    if x_scaled < 0 {
        abs_x = -x_scaled;
    }

    if abs_x > scale * 5 {
        if x_scaled > 0 {
            scale * 148
        } else {
            0
        }
    } else {
        let mut result = scale;
        let mut x_power = x_scaled;
        let mut factorial: i64 = 1;

        for i in 1..15 {
            factorial *= i;
            result += x_power / factorial;
            x_power = (x_power * x_scaled) / scale;
        }

        result
    }
}

pub fn daily_max_drawdown(log_returns: [i64; ARRAY_SIZE], actual_len: u32) -> i64 {
    let mut max_drawdown_decimal: i64 = 0;

    if actual_len > 0 {
        let mut cumulative_sum: i64 = 0;
        let mut running_max: i64 = 0;

        for i in 0..ARRAY_SIZE {
            if (i as u32) < actual_len {
                cumulative_sum += log_returns[i];

                if cumulative_sum > running_max {
                    running_max = cumulative_sum;
                }

                let delta_scaled = cumulative_sum - running_max;
                if delta_scaled < 0 {
                    let exp_delta = exp_scaled(delta_scaled);
                    let drawdown = SCALE - exp_delta;
                    if drawdown > max_drawdown_decimal {
                        max_drawdown_decimal = drawdown;
                    }
                }
            }
        }
    }
    max_drawdown_decimal
}

#[test]
fn test_drawdown_all_positive() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..10 {
        returns[i] = 100;
    }

    let result = daily_max_drawdown(returns, 10);
    assert(result == 0);
}

#[test]
fn test_drawdown_simple_case() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;
    returns[2] = -300;
    returns[3] = 200;

    let result = daily_max_drawdown(returns, 4);
    assert(result == 800);
}

#[test]
fn test_drawdown_multiple_peaks() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;
    returns[2] = 800;
    returns[3] = -1200;
    returns[4] = 400;

    let result = daily_max_drawdown(returns, 5);
    let expected = 1200;
    let tolerance = 100;
    assert((result >= expected - tolerance) & (result <= expected + tolerance));
}

#[test]
fn test_drawdown_all_negative() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = -100;
    }

    let result = daily_max_drawdown(returns, 5);
    let expected = 500;
    let tolerance = 20;
    assert((result >= expected - tolerance) & (result <= expected + tolerance));
}

#[test]
fn test_drawdown_ptn_example() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000000;
    returns[1] = -2000000;
    returns[2] = 1500000;
    let result = daily_max_drawdown(returns, 3);
    let expected = 1960625;
    let diff = if result > expected {
        result - expected
    } else {
        expected - result
    };
    assert(diff < 50000);
}

#[test]
fn test_exp_scaled_approx() {
    let result_neg = exp_scaled(-5000000);
    let expected_neg = 95122942i64;
    let diff_neg = if result_neg > expected_neg {
        result_neg - expected_neg
    } else {
        expected_neg - result_neg
    };
    assert(diff_neg < 1000);

    let result_pos = exp_scaled(100000);
    let expected_pos = 100100050i64;
    let diff_pos = if result_pos > expected_pos {
        result_pos - expected_pos
    } else {
        expected_pos - result_pos
    };
    assert(diff_pos < 1000);
}

#[test]
fn test_drawdown_small_delta_accuracy() {
    let result = exp_scaled(-100000);
    let expected = 99900050i64;
    let diff = if result > expected {
        result - expected
    } else {
        expected - result
    };
    assert(diff < 1000);
}

#[test]
fn test_drawdown_zero_variance() {
    let mut returns = [0; ARRAY_SIZE];
    let result = daily_max_drawdown(returns, 60);
    assert(result == 0);
}

#[test]
fn test_drawdown_all_negative_small() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = -1000000;
    }
    let result = daily_max_drawdown(returns, 5);
    let expected = 4877058i64;
    let diff = if result > expected {
        result - expected
    } else {
        expected - result
    };
    assert(diff < 1000);
}
