# --- build stage ---
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
COPY tsconfig.json ./
COPY vite.config.ts ./
COPY postcss.config.cjs ./
COPY tailwind.config.cjs ./
RUN npm ci || npm install
COPY index.html ./
# если у тебя нет папки public — эту строку можно опустить
# COPY public ./public
COPY src ./src

# ВАЖНО: сообщаем Vite, что база путей = /ui/
RUN npm run build -- --base=/ui/

# --- runtime stage ---
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
# SPA fallback (чтобы всегда отдавать index.html)
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
