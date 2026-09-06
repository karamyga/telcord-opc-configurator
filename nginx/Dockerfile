FROM nginx:1.27-alpine

COPY backend/app/static/index.html /usr/share/nginx/html/index.html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
