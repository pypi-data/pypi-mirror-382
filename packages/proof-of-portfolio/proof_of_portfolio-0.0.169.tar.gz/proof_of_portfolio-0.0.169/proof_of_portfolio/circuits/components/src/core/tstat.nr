use crate::utils::{
    constants::{SCALE, STATISTICAL_CONFIDENCE_MINIMUM_N, STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE},
    sqrt::sqrt,
};

pub fn statistical_confidence(
    actual_len: u32,
    bypass_confidence: bool,
    avg_daily_return: i64,
    variance_val: i64,
    noconfidence_value: i64,
    minimum_n: u32,
) -> i64 {
    if !bypass_confidence & actual_len < minimum_n {
        if actual_len < 2 {
            noconfidence_value
        } else {
            compute_t_statistic(
                actual_len,
                avg_daily_return,
                variance_val,
                noconfidence_value,
            )
        }
    } else {
        compute_t_statistic(
            actual_len,
            avg_daily_return,
            variance_val,
            noconfidence_value,
        )
    }
}

fn compute_t_statistic(
    actual_len: u32,
    avg_daily_return: i64,
    variance_val: i64,
    noconfidence_value: i64,
) -> i64 {
    let avg = avg_daily_return;
    let var = variance_val;

    if var <= 0 {
        noconfidence_value
    } else {
        let std_dev = sqrt(var as u64) as i64;
        let n_sqrt = sqrt(actual_len as u64) as i64;
        let standard_error = std_dev / n_sqrt;

        if standard_error == 0 {
            SCALE
        } else {
            (avg * SCALE) / standard_error
        }
    }
}

#[test]
fn test_tstat_normal_case() {
    let avg = 320;
    let variance_val = 200000;
    let result = statistical_confidence(
        5,
        false,
        avg,
        variance_val,
        STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE,
        STATISTICAL_CONFIDENCE_MINIMUM_N,
    );
    assert(result > 0);
}

#[test]
fn test_tstat_insufficient_data() {
    let avg = 1000;
    let variance_val = 0;

    let result = statistical_confidence(
        1,
        false,
        avg,
        variance_val,
        STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE,
        STATISTICAL_CONFIDENCE_MINIMUM_N,
    );
    assert(result == STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE);
}

#[test]
fn test_tstat_zero_variance() {
    let avg = 100;
    let variance_val = 0;

    let result = statistical_confidence(
        5,
        false,
        avg,
        variance_val,
        STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE,
        STATISTICAL_CONFIDENCE_MINIMUM_N,
    );
    assert(result == STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE);
}

#[test]
fn test_tstat_exactly_two_samples() {
    let avg = 250;
    let variance_val = 1125000;

    let result = statistical_confidence(
        2,
        false,
        avg,
        variance_val,
        STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE,
        STATISTICAL_CONFIDENCE_MINIMUM_N,
    );
    assert(result > 0);
}

#[test]
fn test_tstat_bypass_confidence_true() {
    let avg = 100;
    let variance_val = 500000;

    let result = statistical_confidence(
        30,
        true,
        avg,
        variance_val,
        STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE,
        STATISTICAL_CONFIDENCE_MINIMUM_N,
    );

    let expected = 70921985;
    let tolerance = 10000;

    let diff = if result > expected {
        result - expected
    } else {
        expected - result
    };

    assert(diff <= tolerance);
    assert(result > 0);
}

#[test]
fn test_tstat_bypass_confidence_false_insufficient() {
    let avg = 200;
    let variance_val = 400000;

    let result = statistical_confidence(
        30,
        false,
        avg,
        variance_val,
        STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE,
        STATISTICAL_CONFIDENCE_MINIMUM_N,
    );

    let expected = 158730158;
    let tolerance = 10000;
    let diff = if result > expected {
        result - expected
    } else {
        expected - result
    };
    assert(diff <= tolerance);
}

#[test]
fn test_tstat_bypass_confidence_false_sufficient() {
    let avg = 150;
    let variance_val = 300000;

    let result = statistical_confidence(
        75,
        false,
        avg,
        variance_val,
        STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE,
        STATISTICAL_CONFIDENCE_MINIMUM_N,
    );

    let expected = 220588235;
    let tolerance = 25000;

    let diff = if result > expected {
        result - expected
    } else {
        expected - result
    };

    assert(diff <= tolerance);
    assert(result > 0);
}
