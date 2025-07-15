#!/bin/bash
# Generate self-signed TLS certificates for MQTT broker
CERT_DIR="config/certs"
mkdir -p "$CERT_DIR"

echo "Generating CA key and cert..."
openssl genrsa -out "$CERT_DIR/ca.key" 2048
openssl req -new -x509 -days 3650 -key "$CERT_DIR/ca.key"     -out "$CERT_DIR/ca.crt"     -subj "/CN=EdgeWatch-CA/O=EdgeWatch/C=MY"

echo "Generating server key and cert..."
openssl genrsa -out "$CERT_DIR/server.key" 2048
openssl req -new -key "$CERT_DIR/server.key"     -out "$CERT_DIR/server.csr"     -subj "/CN=edgewatch.local/O=EdgeWatch/C=MY"
openssl x509 -req -days 3650     -in "$CERT_DIR/server.csr"     -CA "$CERT_DIR/ca.crt" -CAkey "$CERT_DIR/ca.key"     -CAcreateserial -out "$CERT_DIR/server.crt"

echo "Certs generated in $CERT_DIR/"
