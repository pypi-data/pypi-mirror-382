use crate::utils::constants::SCALE;

pub fn mdd_augmentation(drawdown_decimal: i64, max_drawdown_percentage: i64) -> i64 {
    if (drawdown_decimal <= 0) | (drawdown_decimal >= SCALE) {
        0
    } else {
        let dd_percent = (drawdown_decimal * 100) / SCALE;

        if dd_percent <= 0 | dd_percent >= max_drawdown_percentage {
            0
        } else {
            // Risk normalization formula: penalizes drawdown more heavily
            let penalty = (5 * dd_percent) / 2;  // 2.5 * dd_percent
            let remaining = max_drawdown_percentage - penalty;
            (remaining * SCALE) / max_drawdown_percentage
        }
    }
}

pub fn risk_normalization(drawdown_decimal: i64, max_drawdown_percentage: i64) -> i64 {
    mdd_augmentation(drawdown_decimal, max_drawdown_percentage)
}

#[test]
fn test_risk_normalization_zero_drawdown() {
    let result = risk_normalization(0, 10);
    assert(result == 0);
}

#[test]
fn test_risk_normalization_high_drawdown() {
    let drawdown_15_percent = (15 * SCALE) / 100;
    let result = risk_normalization(drawdown_15_percent, 10);
    assert(result == 0);
}

#[test]
fn test_risk_normalization_low_drawdown() {
    let drawdown_2_percent = (2 * SCALE) / 100;
    let result = risk_normalization(drawdown_2_percent, 10);
    let expected = SCALE / 2;
    assert(result == expected);
}

#[test]
fn test_risk_normalization_max_threshold() {
    let drawdown_10_percent = (10 * SCALE) / 100;
    let result = risk_normalization(drawdown_10_percent, 10);
    assert(result == 0);
}
