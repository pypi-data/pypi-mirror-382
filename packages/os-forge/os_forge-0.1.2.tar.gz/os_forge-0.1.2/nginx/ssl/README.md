# SSL Certificates for Policy Guard

This directory contains SSL certificates for HTTPS configuration.

## For Development

You can generate self-signed certificates for development:

```bash
# Generate private key
openssl genrsa -out key.pem 2048

# Generate certificate
openssl req -new -x509 -key key.pem -out cert.pem -days 365 -subj "/CN=policy-guard.local"
```

## For Production

Replace these files with your actual SSL certificates:

- `cert.pem` - Your SSL certificate
- `key.pem` - Your private key
- `chain.pem` - Certificate chain (if applicable)

## Security Note

Never commit real SSL certificates to version control. Use environment variables or secret management systems in production.

