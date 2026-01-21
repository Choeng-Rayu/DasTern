# ===========================================
# DasTern Backend - Next.js
# Node 20 LTS (required by Next.js)
# ===========================================

FROM node:20-slim

WORKDIR /app

# Copy package files first (better caching)
COPY package*.json ./

# Install dependencies (use install instead of ci for flexibility)
RUN npm install --prefer-offline --no-audit

# Copy source
COPY . .

EXPOSE 3000

# Development mode
CMD ["npm", "run", "dev"]
