#!/usr/bin/env python3
"""
ZeroMQ XPUB/XSUB message proxy.
All services connect (not bind) to this proxy.
Publishers -> XSUB (port 5556) -> XPUB (port 5555) -> Subscribers.
"""
import zmq, signal, sys, logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger("zmq_proxy")

PUB_ADDR = "tcp://*:5555"  # subscribers connect here
SUB_ADDR = "tcp://*:5556"  # publishers connect here

def run():
    ctx     = zmq.Context()
    xpub    = ctx.socket(zmq.XPUB)
    xsub    = ctx.socket(zmq.XSUB)
    xpub.bind(PUB_ADDR)
    xsub.bind(SUB_ADDR)

    def shutdown(*_):
        logger.info("zmq_proxy shutting down")
        xpub.close(); xsub.close(); ctx.term()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT,  shutdown)

    logger.info(f"ZMQ proxy running: PUB={PUB_ADDR} SUB={SUB_ADDR}")
    try:
        zmq.proxy(xpub, xsub)
    except zmq.ZMQError as e:
        if e.errno != zmq.ETERM:
            raise

if __name__ == "__main__":
    run()
