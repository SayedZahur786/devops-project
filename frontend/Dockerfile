# Stage 1: build the React app with Node
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY index.html vite.config.js ./
COPY src/ src/
RUN npm run build

# Stage 2: serve the static build with Nginx (no Node tooling in the runtime image)
FROM nginx:1.29-alpine
RUN apk upgrade --no-cache
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
ENV BACKEND_HOST=backend
COPY --from=build /app/dist /usr/share/nginx/html

# Run Nginx as a non-root user
RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/log/nginx /etc/nginx/conf.d \
    && touch /var/run/nginx.pid && chown nginx:nginx /var/run/nginx.pid
USER nginx

EXPOSE 80
