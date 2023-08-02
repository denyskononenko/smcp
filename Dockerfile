# build react front end 
FROM node:latest as build-step
WORKDIR /smcp
ENV PATH /smcp/node_modules/.bin:$PATH
COPY package.json ./
COPY ./src ./src 
COPY ./public ./public
RUN yarn install 
RUN yarn build 
# build flask backend
FROM python:3.8
WORKDIR /smcp
COPY --from=build-step /smcp/build ./build
# copy backend files
RUN mkdir ./backend
RUN mkdir ./backend/cif/
COPY backend/cif/test backend/cif/test 
COPY backend/requirements.txt backend/.flaskenv  backend/api.py ./backend/
COPY backend/ionrad.json backend/core.py backend/utils.py backend/zernike3d.py backend/make_basis.py ./backend/
# copy ml core files
RUN mkdir ./backend/ml
COPY backend/ml/envs_r4_f0.1_Hopt backend/ml/envs_r4_f0.1_Hopt
COPY backend/ml/serialize_model.py backend/ml/dataset.py ./backend/ml/ 
RUN mkdir ./backend/ml/model
# install dependencies
RUN pip3 install -U pip
RUN pip3 install -r ./backend/requirements.txt
# train and serialize ml model
RUN python3 ./backend/ml/serialize_model.py
# copy basis 
# COPY backend/basis backend/basis
RUN python3 ./backend/make_basis.py

ENV FLASK_ENV production

EXPOSE 3000
WORKDIR /smcp/backend
CMD ["gunicorn", "--timeout", "800", "-b", ":3000", "api:app"]
