FROM node:22.14-slim

WORKDIR /app

COPY package*.json ./

RUN npm ci --omit=dev

COPY . .

EXPOSE 5001

CMD ["node", "index.js"]

