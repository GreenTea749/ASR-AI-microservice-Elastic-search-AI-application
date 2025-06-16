# search-ui/Dockerfile
FROM node:18-alpine AS build
ARG REACT_APP_ES_HOST=http://localhost:9200
ENV REACT_APP_ES_HOST=$REACT_APP_ES_HOST
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /srv
RUN npm install -g serve
COPY --from=build /app/build ./build
EXPOSE 3000
CMD ["serve", "-s", "build", "-l", "3000"]
