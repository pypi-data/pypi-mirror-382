use crate::utils::constants::{ARRAY_SIZE, SCALE};

fn exp_decay_scaled(neg_x_scaled: i64) -> i64 {
    let scale: i64 = 100000;

    if neg_x_scaled < -200000 {
        scale / 1000
    } else {
        let x_pow_2 = neg_x_scaled * neg_x_scaled;
        let x_pow_3 = x_pow_2 * neg_x_scaled;

        let term1 = neg_x_scaled;
        let term2 = x_pow_2 / (2 * scale);
        let term3 = x_pow_3 / (6 * scale * scale);

        scale + term1 + term2 + term3
    }
}

pub fn weighting_distribution(
    actual_len: u32,
    weighted_decay_max: i64,
    weighted_decay_min: i64,
    weighted_decay_rate: i64,
) -> [i64; ARRAY_SIZE] {
    let mut weights = [0; ARRAY_SIZE];
    let max_weight = weighted_decay_max;
    let min_weight = weighted_decay_min;
    let decay_rate = weighted_decay_rate;
    let weight_range = max_weight - min_weight;
    let scale = SCALE;

    for i in 0..ARRAY_SIZE {
        if (i as u32) < actual_len {
            let position_from_newest = (actual_len - 1) - (i as u32);
            let neg_x_scaled = -(decay_rate * (position_from_newest as i64));
            let exp_val_scaled = exp_decay_scaled(neg_x_scaled);

            let weighted_val = (weight_range * exp_val_scaled) / scale;
            weights[i] = min_weight + weighted_val;
        }
    }

    weights
}
