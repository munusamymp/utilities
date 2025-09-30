#!/bin/bash

set -e

# === Configuration ===
SECRET_NAME=$1
REGION="us-east-1"
PRIVATE_KEY_FILE="rsa_private_key.p8"
PUBLIC_KEY_FILE="rsa_public_key.pem"
PASSWORD=""  # You should prompt or load this securely

# === Generate private key ===
echo "Generating encrypted RSA private key..."
openssl genrsa 2048 | openssl pkcs8 -topk8 -v2 des3 -inform PEM -out "$PRIVATE_KEY_FILE"

# === Extract public key from private key ===
echo "Generating public key from private key..."
openssl rsa -in "$PRIVATE_KEY_FILE" -pubout -out "$PUBLIC_KEY_FILE"

# === Read contents ===
PRIVATE_KEY_CONTENT=$(<"$PRIVATE_KEY_FILE")
PUBLIC_KEY_CONTENT=$(<"$PUBLIC_KEY_FILE")

# === Prepare JSON payload ===
SECRET_STRING=$(jq -n \
  --arg private_key "$PRIVATE_KEY_CONTENT" \
  --arg public_key "$PUBLIC_KEY_CONTENT" \
  '{private_key: $private_key, public_key: $public_key}'
)

# === Upload to AWS Secrets Manager ===
if aws secretsmanager describe-secret --secret-id "$SECRET_NAME" --region "$REGION" &> /dev/null; then
  echo "Secret $SECRET_NAME already exists. Updating..."
  aws secretsmanager put-secret-value \
    --secret-id "$SECRET_NAME" \
    --region "$REGION" \
    --secret-string "$SECRET_STRING"
else
  echo "Creating new secret $SECRET_NAME..."
  aws secretsmanager create-secret \
    --name "$SECRET_NAME" \
    --region "$REGION" \
    --secret-string "$SECRET_STRING"
fi

echo "Key pair stored in AWS Secrets Manager under secret name: $SECRET_NAME"

# Optional: Clean up key files
rm -f "$PRIVATE_KEY_FILE" "$PUBLIC_KEY_FILE"

