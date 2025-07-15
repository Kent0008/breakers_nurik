FROM node:18-alpine

WORKDIR /app

# Копирование зависимостей
COPY package*.json ./
RUN npm install

# Копирование исходного кода
COPY . .

# Экспорт порта
EXPOSE 3000

# Команда запуска
CMD ["npm", "run", "dev"] 