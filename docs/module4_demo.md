# Module 4 demo & explanation notes

## 90-second demo walkthrough

1. **Purpose:** "Unlike the first three modules, we see the response and estimate the sensor parameters backward."
2. **New Sensor:** Generates first-order or second-order parameters privately in browser Python and samples the response with slight Gaussian noise.
3. **Three challenge modes:** First-order step, first-order **steady-state sine**, and second-order step. For the sine, the unit-amplitude input and known angular frequency are displayed so the two unknown parameters can be estimated.
4. **First-order step:** final value gives K; the 63.2% crossing time gives tau.
5. **Sine:** use phase lag to estimate tau; use output/input amplitude ratio and tau to estimate K.
6. **Second-order step:** overshoot estimates damping ζ; first peak time plus ζ estimates natural frequency ωn.
7. **Submit Guess:** The Python model computes the guessed prediction, reveals the true values, shows three overlapping curves (plus sine input if present), and calculates a fair score.
8. **Session:** The score is cumulative, with average and completed rounds. New Sensor starts another round; a second submission cannot change the score for the previous round.
9. **Hint:** Explains how to estimate without giving the true parameter values away.

## Questions likely to come up

**Q: What does K mean?**  A: Steady-state sensitivity/gain. For a unit step, output eventually approaches K. For a sine, output amplitude is further reduced by the dynamic magnitude ratio M.

**Q: What does tau mean?**  A: A first-order time constant. At t=tau a zero-initial-condition step reaches 1−1/e≈63.2% of its final value. Larger tau means a slower time response and greater sine phase lag at a fixed ω.

**Q: What are ζ and ωn?**  A: ζ determines damping/overshoot; ωn is natural frequency and affects the response timing. We choose underdamped sensors so both can be estimated using overshoot and the first peak.

**Q: Why add noise?**  A: Real measurements are rarely perfectly smooth; small Gaussian noise makes estimation closer to a measurement task. The hidden analytical response is available only at reveal time.

**Q: How does sine identification work?**  A: The input is shown as `sin(ωt)` with known ω. The sensor output is `K M sin(ωt+φ)`; `φ = −atan(ωτ)`, and `M=1/sqrt(1+(ωτ)^2)`. The input and output peaks allow estimating φ and the amplitude ratio, hence τ and K. The plotted sine is the steady-state output; the start-up transient is assumed decayed.

**Q: Why can the student score 100 even if not exactly correct?**  A: The homework explicitly says guesses within 10% earn full marks. We then provide smoothly decreasing partial credit to be fair to near-misses.

**Q: How is score calculated?**  A: Each parameter contributes half of the round score. Error percent is `100*abs(guess−true)/true`, full score at ≤10%, zero at ≥100%, linear in-between.

**Q: How are zero parameters handled?**  A: All randomly generated true parameters are strictly greater than zero. Therefore relative error always has a valid denominator. User guesses for physical parameters must also be positive; ζ must lie strictly between 0 and 1.

**Q: Does this run offline?**  A: The site needs internet to load Pyodide and Plotly libraries via CDN, but all computation runs locally in the visitor's browser. No server/database or login is needed.

**Q: How is user fairness protected?**  A: The noiseless true curve and parameters are never sent to the displayed graph before submission. A submitted round gets locked, and clicking New Sensor begins the next round while preserving the session total.

## Practical live test

- Demonstrate a First Order step and its 63.2% point by reading the curve.
- Click New Sensor until a First Order Sine challenge appears; show input sine and stated ω.
- Demonstrate a second-order case and estimate ζ from overshoot.
- Submit guess and point out orange predicted vs blue actual model.
- Show score change for one round; then New Sensor and show session total remains.
- Resize to mobile or show the site on a real phone.

## Honest limits

- Generated parameters are hidden from the page UI, not cryptographically secure against browser developer tools. This is an educational demonstration, not an anti-cheat exam platform.
- Second-order cases are limited to the underdamped regime. Modules 1–3 already cover the full response families, while this challenge focuses on estimable cases.
- Sine response is steady-state, so the signal at t=0 need not be zero; this is intentional and follows frequency-response theory.
