# ===========================================
# DasTern Backend - Next.js
# Node 18 LTS (stable + safe)
# ===========================================

FROM node:18.19.0-slim

WORKDIR /app

# Copy package files first (better caching)
COPY package*.json ./

# Deterministic install
RUN npm ci

# Copy source
COPY . .

EXPOSE 3000

# Development mode
CMD ["npm", "run", "dev"]
