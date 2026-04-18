# ── Stage 1: dependencies ─────────────────────────────────────────────
FROM node:20-bullseye AS deps
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

# ── Stage 2: builder ──────────────────────────────────────────────────
FROM node:20-bullseye AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# ── Stage 3: production runtime ───────────────────────────────────────
FROM node:20-bullseye AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

CMD ["node", "server.js"]