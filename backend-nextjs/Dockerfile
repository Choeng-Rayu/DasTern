# ===========================================
# DasTern Backend - Next.js
# Node 20 LTS (required by Next.js)
# ===========================================

FROM node:20-slim

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
