use crate::utils::{constants::{SCALE, SHARPE_STDDEV_MINIMUM}, sqrt::sqrt};

pub fn sharpe(
    actual_len: u32,
    bypass_confidence: bool,
    variance_val: i64,
    ann_excess_return_val: i64,
    noconfidence_value: i64,
    minimum_n: u32,
    python_sharpe: i64,
) -> i64 {
    println(
        f"[SHARPE] Entry: actual_len={actual_len}, bypass_confidence={bypass_confidence}, minimum_n={minimum_n}",
    );
    let not_bypass = !bypass_confidence;
    let len_too_small = actual_len < minimum_n;
    println(
        f"[SHARPE] Condition check: not_bypass={not_bypass}, len_too_small={len_too_small}",
    );

    let result = if !bypass_confidence & actual_len < minimum_n {
        println(
            f"[SHARPE] Taking noconfidence path: returning {noconfidence_value}",
        );
        noconfidence_value
    } else {
        println(f"[SHARPE] Taking calculation path");
        let excess_return = ann_excess_return_val;
        println(f"[SHARPE-CALC] excess_return={excess_return}");
        println(f"[SHARPE-CALC] variance_val (input)={variance_val}");
        println(f"[SHARPE-CALC] actual_len={actual_len}");

        let volatility = if actual_len < 2 {
            println(f"[SHARPE-CALC] Using fallback volatility: {SCALE}");
            SCALE
        } else {
            println(f"[SHARPE-CALC] Step 1: Converting variance to annualized");
            let scaled_annualized_variance = (variance_val as u64) * 365;
            println(
                f"[SHARPE-CALC] variance_val={variance_val}, scaled_annualized_variance={scaled_annualized_variance}",
            );

            println(f"[SHARPE-CALC] Step 2: Taking square root");
            let volatility_precise = sqrt(scaled_annualized_variance);
            println(f"[SHARPE-CALC] volatility_precise={volatility_precise}");

            println(f"[SHARPE-CALC] Step 3: Converting back to i64");
            let vol_as_i64 = volatility_precise as i64;
            println(f"[SHARPE-CALC] vol_as_i64={vol_as_i64}");

            vol_as_i64
        };

        println(
            f"[SHARPE-CALC] Step 5: Checking minimum volatility constraint",
        );
        let effective_volatility = if volatility < SHARPE_STDDEV_MINIMUM {
            println(
                f"[SHARPE-CALC] Volatility {volatility} < minimum {SHARPE_STDDEV_MINIMUM}, using minimum",
            );
            SHARPE_STDDEV_MINIMUM
        } else {
            println(f"[SHARPE-CALC] Using calculated volatility: {volatility}");
            volatility
        };

        println(f"[SHARPE-CALC] Step 6: Computing final Sharpe ratio");
        let numerator = excess_return * SCALE;
        println(
            f"[SHARPE-CALC] numerator = {excess_return} * {SCALE} = {numerator}",
        );
        let calculated = numerator / effective_volatility;
        println(
            f"[SHARPE-CALC] calculated = {numerator} / {effective_volatility} = {calculated}",
        );

        println(f"[SHARPE-CALC] Step 7: Comparing with Python value");
        println(f"[SHARPE-CALC] python_sharpe={python_sharpe}");
        let diff_value = if calculated > python_sharpe {
            calculated - python_sharpe
        } else {
            python_sharpe - calculated
        };
        println(
            f"[SHARPE-CALC] calculated={calculated}, python={python_sharpe}, diff={diff_value}",
        );

        println(
            f"[SHARPE] excess_return={excess_return}, variance={variance_val}, volatility={volatility}, eff_vol={effective_volatility}",
        );
        println(
            f"[SHARPE] calculated={calculated}, python={python_sharpe}, diff={diff_value}",
        );
        calculated
    };

    let tolerance: i64 = 50000;
    let diff = if result > python_sharpe {
        result - python_sharpe
    } else {
        python_sharpe - result
    };

    println(
        f"[SHARPE] Final: result={result}, python={python_sharpe}, diff={diff}, tolerance={tolerance}",
    );
    assert(diff <= tolerance);

    python_sharpe
}
