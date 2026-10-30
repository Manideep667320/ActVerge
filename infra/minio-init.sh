#!/usr/bin/env bash
# infra/minio-init.sh
# Initialises the MinIO bucket required by ActVerge.
# Run once after `docker compose up -d minio` completes its health check.
#
# Usage:
#   bash infra/minio-init.sh
#
# Requires: mc (MinIO Client) available in PATH, or run inside the minio container.

set -euo pipefail

MINIO_ALIAS="local"
MINIO_ENDPOINT="http://minio:9000"
MINIO_ACCESS_KEY="${MINIO_ROOT_USER:-minioadmin}"
MINIO_SECRET_KEY="${MINIO_ROOT_PASSWORD:-minioadmin}"
BUCKET_NAME="${MINIO_BUCKET:-actverge-artifacts}"

echo "==> Waiting for MinIO to be ready..."
until mc alias set "${MINIO_ALIAS}" "${MINIO_ENDPOINT}" "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}" > /dev/null 2>&1; do
  echo "    MinIO not ready yet — retrying in 3s..."
  sleep 3
done
echo "    MinIO is ready."

echo "==> Creating bucket: ${BUCKET_NAME}"
if mc ls "${MINIO_ALIAS}/${BUCKET_NAME}" > /dev/null 2>&1; then
  echo "    Bucket '${BUCKET_NAME}' already exists — skipping creation."
else
  mc mb "${MINIO_ALIAS}/${BUCKET_NAME}"
  echo "    Bucket '${BUCKET_NAME}' created."
fi

echo "==> Setting anonymous download policy on '${BUCKET_NAME}'..."
mc anonymous set download "${MINIO_ALIAS}/${BUCKET_NAME}"
echo "    Policy set: public read (download) on ${BUCKET_NAME}."

echo ""
echo "✅  MinIO initialisation complete."
echo "    Console: http://localhost:9001  (user: ${MINIO_ACCESS_KEY})"
