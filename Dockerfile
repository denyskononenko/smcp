# build react front end 
FROM node:latest as build-step
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY package.json ./
COPY ./src ./src 
COPY ./public ./public
RUN yarn install 
RUN yarn build 

# build flask backend
# FROM python:3.9
# WORKDIR /app
# COPY --from=build-step /app/build ./build

# RUN mkdir ./backend
# COPY backend/requirements.txt backend/.flaskenv  backend/api.py ./backend/
# COPY backend/ionrad.json backend/core.py backend/utils.py backend/zernike3d.py ./backend/
# RUN pip install -r ./backend/requirements.txt
# ENV FLASK_ENV production

EXPOSE 3000
# WORKDIR /backend/api
