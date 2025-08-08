# EdgeWatch Acceptance Test Results

Date: August 7-8, 2025

| Test | Requirement | Result | Status |
|------|-------------|--------|--------|
| Prone detection (mannequin) | 9/10 scenarios | 9/10 | PASS |
| Face occlusion (daytime) | 9/10 scenarios | 9/10 | PASS |
| Face occlusion (IR mode) | 9/10 scenarios | 8/10 | MARGINAL |
| Respiratory rate accuracy | ±4 bpm in 80% | ±4 in 82% | PASS |
| Temp accuracy | ±1°C vs reference | ±0.8°C | PASS |
| Humidity accuracy | ±5% RH vs reference | ±4.2% RH | PASS |
| False CRITICAL alerts | < 3 per 8-hour session | 2.1 avg | PASS |
| Alert latency | < 8s in 95% of tests | P95 = 7.2s | PASS |
| No video/audio transmitted | Packet capture audit | Zero packets | PASS |
| Continuous operation | 10-hour uptime | 11 hours | PASS |

## Notes
- IR mode occlusion marginally below 9/10 target. Algorithm improved from 6/10 to 8/10.
- Respiratory rate: 82% of 30s windows within ±4 bpm (metronome test at 20,30,40 bpm).
- False CRITICAL rate: 2.1 per 8hr simulation. Under threshold of 3.
