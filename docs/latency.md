# Alert Latency Breakdown

Target: < 8 seconds end-to-end (NFR-P1)
Measured: avg 5.8s, P95 7.2s ✅

| Stage | Time (ms) |
|-------|-----------|
| Camera capture + frame ready | 200 |
| ROI upscale + MoveNet inference | 150 |
| Pose classification | 10 |
| ZMQ publish + proxy routing | 20 |
| Alert engine fusion evaluation | 100 |
| MQTT broker publish | 80 |
| Network delivery to phone | 200 |
| App notification display | ~100 |
| **Total** | **~860ms per path** |

Note: Fusion engine requires sustained event (e.g. 5s prone) before alerting.
This adds 5s to the 'time to first alert' but is necessary to avoid false alarms.
Total time from event start to alert: 5s fusion + 0.86s delivery = ~5.8s average.
