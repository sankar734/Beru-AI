# Stage 1: Build React 19 / Vite Application
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY apps/web/package*.json ./apps/web/

RUN npm ci

COPY apps/web ./apps/web

RUN npm run build --workspace=apps/web

# Stage 2: Serve static bundle via Nginx
FROM nginx:alpine-slim

COPY --from=builder /app/apps/web/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

HEALTHCHECK --interval=20s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
