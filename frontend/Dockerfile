FROM node:12-alpine

WORKDIR /frontend_app

COPY package.json ./
COPY package-lock.json ./

RUN npm ci --also=dev

COPY . .

CMD ["./node_modules/.bin/parcel", "watch", "bundles-src/index.js", "--dist-dir", "bundles", "--public-url='./'"]
