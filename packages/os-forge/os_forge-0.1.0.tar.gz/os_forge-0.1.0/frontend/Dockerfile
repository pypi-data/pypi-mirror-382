# -------- Base Node image --------
    FROM node:18-alpine AS base
    WORKDIR /app
    
    # -------- Dependencies stage --------
    FROM base AS deps
    RUN apk add --no-cache libc6-compat
    COPY package.json package-lock.json* ./
    # Install ALL dependencies (needed for Next.js build)
    RUN npm ci && npm cache clean --force
    
    # -------- Build stage --------
    FROM base AS builder
    WORKDIR /app
    COPY --from=deps /app/node_modules ./node_modules
    COPY . .
    RUN npm run build
    
    # -------- Production image --------
    FROM nginx:1.25-alpine AS production
    
    # Install curl for healthcheck + debugging
    RUN apk add --no-cache curl
    
    # Create non-root user
    RUN addgroup -g 1001 -S osforge && \
        adduser -S -u 1001 -h /app -s /sbin/nologin -G osforge osforge
    
    WORKDIR /app
    
    # Copy Next.js standalone build output
    COPY --from=builder /app/.next/standalone ./ 
    COPY --from=builder /app/.next/static ./.next/static 
    COPY --from=builder /app/public ./public
    
    # -------------------------------
    # Copy nginx configuration
    # (Make sure nginx.conf exists in your repo at project root)
    # -------------------------------
    COPY nginx.conf /etc/nginx/nginx.conf
    
    # -------------------------------
    # Copy startup script
    # (Make sure start.sh exists in your repo at project root)
    # -------------------------------
    COPY start.sh /app/start.sh
    RUN chmod +x /app/start.sh && chown osforge:osforge /app/start.sh
    
    # Fix nginx permissions
    RUN mkdir -p /var/cache/nginx /var/log/nginx /var/run && \
        chown -R osforge:osforge /var/cache/nginx /var/log/nginx /var/run
    
    # Switch to non-root user
    USER osforge
    
    # Environment variables
    ENV NODE_ENV=production \
        PORT=3001 \
        HOSTNAME=127.0.0.1
    
    # Expose port
    EXPOSE 3000
    
    # Health check
    HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
        CMD curl -f http://localhost:3000/health || exit 1
    
    # Labels for metadata
    LABEL maintainer="OS Forge Team" \
          version="1.0.0" \
          description="OS Forge - Multi-Platform System Hardening Tool Frontend" \
          org.opencontainers.image.title="OS Forge Frontend" \
          org.opencontainers.image.description="Next.js frontend with nginx for system hardening" \
          org.opencontainers.image.version="1.0.0" \
          org.opencontainers.image.source="https://github.com/your-org/policy-guard"
    
    # Use startup script
    CMD ["/app/start.sh"]
    