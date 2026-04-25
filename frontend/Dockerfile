FROM node:20-alpine AS builder

WORKDIR /app

ARG NEXT_PUBLIC_API_URL=/api/v1
ARG NEXT_PUBLIC_FLOWER_URL=http://127.0.0.1:5555
ARG NEXT_PUBLIC_BREAKING_TTL_MINUTES=60
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_FLOWER_URL=$NEXT_PUBLIC_FLOWER_URL
ENV NEXT_PUBLIC_BREAKING_TTL_MINUTES=$NEXT_PUBLIC_BREAKING_TTL_MINUTES

# Dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Source
COPY . .

# Build
RUN npm run build

# Production image
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ARG NEXT_PUBLIC_API_URL=/api/v1
ARG NEXT_PUBLIC_FLOWER_URL=http://127.0.0.1:5555
ARG NEXT_PUBLIC_BREAKING_TTL_MINUTES=60
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_FLOWER_URL=$NEXT_PUBLIC_FLOWER_URL
ENV NEXT_PUBLIC_BREAKING_TTL_MINUTES=$NEXT_PUBLIC_BREAKING_TTL_MINUTES

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000

CMD ["node", "server.js"]
