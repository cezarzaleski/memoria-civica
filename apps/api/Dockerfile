FROM node:20-bookworm-slim

WORKDIR /app

COPY package.json package-lock.json tsconfig.json ./
COPY apps ./apps
COPY packages ./packages

RUN npm ci --include=dev

EXPOSE 3000

CMD ["npm", "run", "api:start"]
