# Используем лёгкий nginx
FROM nginx:alpine


# Копируем index.html в корень сервера
COPY index.html /usr/share/nginx/html/index.html


# Открываем порт 80
EXPOSE 80


# Запуск nginx
CMD ["nginx", "-g", "daemon off;"]
