# build env
FROM node:13.12.0-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build

# runtime env
FROM alpine:latest
COPY --from=build /app/build /build
CMD chown -R 33:33 /build && cp -a /build/. /build_result/
