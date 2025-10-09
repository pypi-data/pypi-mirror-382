use components::core::{
    calmar::calmar, drawdown::daily_max_drawdown, omega::omega, sharpe::sharpe, sortino::sortino,
    tstat::statistical_confidence,
};
use components::core::merkle::{
    build_merkle_root, hash_return, hash_signal, merkle_inclusion_check, TradingSignal,
};
use components::utils::{
    ann_excess_return::ann_excess_return,
    average::average,
    constants::{ARRAY_SIZE, MAX_DAYS, MAX_RETURNS, MAX_SIGNALS, MERKLE_DEPTH, SCALE},
    downside_variance::downside_variance,
    variance::variance,
};

fn main(
    hotkey: pub str<48>,
    log_returns: [i64; MAX_DAYS],
    n_returns: u32,
    risk_norm_factor: pub i64,
    daily_pnl: [i64; ARRAY_SIZE],
    n_pnl: u32,
    signals: [TradingSignal; MAX_SIGNALS],
    signals_count: u32,
    path_elements: [[Field; MERKLE_DEPTH]; MAX_SIGNALS],
    path_indices: [[Field; MERKLE_DEPTH]; MAX_SIGNALS],
    signals_merkle_root: pub Field,
    use_weighting: pub bool,
    bypass_confidence: pub bool,
    weights: [i64; ARRAY_SIZE],
    days_in_year: pub i64,
    omega_loss_min: pub i64,
    annual_risk_free: pub i64,
    daily_rf: pub i64,
    omega_noconfidence: pub i64,
    sharpe_noconfidence: pub i64,
    sortino_noconfidence: pub i64,
    calmar_noconfidence: pub i64,
    stat_confidence_noconfidence: pub i64,
    stat_conf_min_n: pub u32,
    python_sharpe: pub i64,
    python_calmar: pub i64,
    python_sortino: pub i64,
    python_omega: pub i64,
) -> pub [Field; 8] {
    // Intentionally unused, hack to trick the compiler into constraining it
    let mut hk = hotkey;
    hk = hotkey;
    // Verify all trading signals are included in the merkle tree
    let mut all_verified = true;
    for i in 0..MAX_SIGNALS {
        if (i as u32) < signals_count {
            let signal_hash = hash_signal(signals[i]);
            let verified = merkle_inclusion_check(
                signal_hash,
                signals_merkle_root,
                path_elements[i],
                path_indices[i],
            );
            all_verified = all_verified & verified;
        }
    }
    assert(all_verified);

    // Build array from returns
    let mut returns_array = [0; ARRAY_SIZE];
    for i in 0..MAX_DAYS {
        if (i as u32) < n_returns {
            returns_array[i] = log_returns[i];
        }
    }

    let weights = if use_weighting {
        weights
    } else {
        // Equal weights when weighting is disabled
        let mut equal_weights = [0; ARRAY_SIZE];
        for i in 0..ARRAY_SIZE {
            equal_weights[i] = SCALE / 1000;
        }
        equal_weights
    };

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
    assert(sum_of_weights != 0);

    let avg_daily_return = average(
        returns_array,
        n_returns,
        weights,
        use_weighting,
        sum_of_weights,
    );
    let variance_val = variance(
        returns_array,
        n_returns,
        1,
        weights,
        use_weighting,
        sum_of_weights,
    );
    let downside_variance_val = downside_variance(
        returns_array,
        n_returns,
        1,
        weights,
        use_weighting,
        daily_rf,
    );
    let ann_excess_return_val = ann_excess_return(
        returns_array,
        n_returns,
        annual_risk_free,
        weights,
        use_weighting,
        days_in_year,
    );

    let avg_daily_pnl = average(daily_pnl, n_pnl, weights, use_weighting, sum_of_weights);

    println(
        f"[MAIN] Input metrics: python_sharpe={python_sharpe}, python_calmar={python_calmar}, python_sortino={python_sortino}, python_omega={python_omega}",
    );
    println(
        f"[MAIN] Basic inputs: n_returns={n_returns}, use_weighting={use_weighting}, bypass_confidence={bypass_confidence}",
    );

    // Show first few returns for debugging
    let r0 = returns_array[0];
    let r1 = returns_array[1];
    let r2 = returns_array[2];
    println(f"[MAIN] First 3 returns: {r0}, {r1}, {r2}");

    println(
        f"[MAIN] Pre-calculations: variance_val={variance_val}, ann_excess_return_val={ann_excess_return_val}, downside_variance_val={downside_variance_val}",
    );

    let sharpe_ratio = sharpe(
        n_returns,
        bypass_confidence,
        variance_val,
        ann_excess_return_val,
        sharpe_noconfidence,
        stat_conf_min_n,
        python_sharpe,
    );
    let dmd = daily_max_drawdown(returns_array, n_returns);
    let calmar_ratio = calmar(
        returns_array,
        n_returns,
        weights,
        use_weighting,
        bypass_confidence,
        days_in_year,
        risk_norm_factor,
        calmar_noconfidence,
        stat_conf_min_n,
        python_calmar,
    );
    let omega_ratio = omega(
        returns_array,
        n_returns,
        weights,
        use_weighting,
        bypass_confidence,
        omega_loss_min,
        omega_noconfidence,
        stat_conf_min_n,
        python_omega,
    );
    let sortino_ratio = sortino(
        n_returns,
        bypass_confidence,
        downside_variance_val,
        ann_excess_return_val,
        sortino_noconfidence,
        stat_conf_min_n,
        python_sortino,
    );
    let stat_confidence = statistical_confidence(
        n_returns,
        bypass_confidence,
        avg_daily_return,
        variance_val,
        stat_confidence_noconfidence,
        stat_conf_min_n,
    );

    // Build merkle root from returns
    let mut leaves = [0; MAX_RETURNS];
    for i in 0..MAX_RETURNS {
        if (i as u32) < n_returns {
            leaves[i] = hash_return(log_returns[i]);
        }
    }
    let computed_returns_root = build_merkle_root(leaves, n_returns);

    [
        (avg_daily_pnl as u64) as Field,
        (sharpe_ratio as u64) as Field,
        (dmd as u64) as Field,
        (calmar_ratio as u64) as Field,
        (omega_ratio as u64) as Field,
        (sortino_ratio as u64) as Field,
        (stat_confidence as u64) as Field,
        computed_returns_root,
    ]
}
