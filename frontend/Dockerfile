# -------- Stage 1: build the static SPA with Vite --------
FROM node:20-alpine AS build

WORKDIR /app

# Install deps from the lockfile for reproducible builds.
COPY package.json package-lock.json ./
RUN npm ci

# Build. VITE_API_BASE defaults to "/api/v1" (a relative path), which the nginx
# stage below proxies to the backend — so the bundle is environment-agnostic.
COPY . .
RUN npm run build

# -------- Stage 2: serve static files with nginx --------
FROM nginx:alpine

# Serve the SPA and reverse-proxy /api to the backend container.
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
