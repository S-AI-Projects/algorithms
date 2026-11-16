# R24-T030 mutation analysis for is_prime

Each cell is the outcome of one test with `secrets.randbelow` replaced by the fixed bases 2, 3, 5, 7. Old = TestRabinMiller; the others are the new TestIsPrimeRegression tests.

| Version | Change | test_is_prime | test_one_is_not_prime | test_fixture_domain_around_1_2_9_11 | test_primes_below_12_with_exclusive_upper_bound | test_no_emitted_prime_has_a_divisor_up_to_its_square_root |
|---|---|---|---|---|---|---|
| original | - | pass | pass | pass | pass | pass |
| P | return condition | pass | fail | fail | fail | fail |
| B | boundary comparison | pass | pass | pass | fail | fail |
| R | return condition | fail | pass | fail | fail | fail |
| W | comparison | fail | pass | fail | fail | fail |

Primary mutant P (`return n == 2 or n == 3` -> `return n <= 3`): it survives the old test, which never calls is_prime below 5, and fails test_one_is_not_prime with an AssertionError. Inputs below 12 where P differs from the original: 0 (original False, mutant True, trial division says prime=False), 1 (original False, mutant True, trial division says prime=False). The reduced input is 1, the fixture value: it has a single divisor, so it is not prime.
