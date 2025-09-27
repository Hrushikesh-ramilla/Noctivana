# Known Issues & Limitations

## Active Issues
1. **BLE reconnection flaky** - On Android, BLE connection drops after ~5 min idle. Keepalive ping workaround works but not robust. Proper connection parameter negotiation needed.
2. **IR mode occlusion accuracy** - 8/10 vs 9/10 target. Thin fabrics with high IR reflectance cause misses. Algorithm improvement needed.
3. **rPPG at ceiling distance** - Heart rate estimate is essentially noise. Fundamental physics: signal too weak at 1.5m. Marked experimental, not used for any alerts.
4. **SGP30 zero reads during long run** - After 2+ hours sensor occasionally returns 0. Workaround: last-known-good value substituted. Root cause: I2C timing or sensor baseline drift.
5. **Session auto-detect false starts** - If room is quiet during day, session may start early. Mitigation: check if small body visible in crib ROI before starting.

## Not Implemented
- mmWave radar (IWR6843AOP) - deferred due to cost ($60) and timeline
- OTA model updates - needs GPG signing infrastructure
- iOS app build - untested (no Apple dev account)
- PDF session export - CSV only
- Multi-crib support
- Web admin dashboard

## Performance Limitations
- Pi4 reaches 72°C after 7+ hours (heatsink installed, manageable)
- rPPG cannot run full-time (CPU headroom)
- Side position detection ~70% accuracy from top-down angle
