FROM node:22-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

ARG VITE_USER_SERVICE_URL=/api/users
ARG VITE_STUDENT_SERVICE_URL=/api/students
ARG VITE_LECTURER_SERVICE_URL=/api/lecturers
ARG VITE_COURSE_SERVICE_URL=/api/courses
ARG VITE_ENROLLMENT_SERVICE_URL=/api/enrollments

ENV VITE_USER_SERVICE_URL=${VITE_USER_SERVICE_URL}
ENV VITE_STUDENT_SERVICE_URL=${VITE_STUDENT_SERVICE_URL}
ENV VITE_LECTURER_SERVICE_URL=${VITE_LECTURER_SERVICE_URL}
ENV VITE_COURSE_SERVICE_URL=${VITE_COURSE_SERVICE_URL}
ENV VITE_ENROLLMENT_SERVICE_URL=${VITE_ENROLLMENT_SERVICE_URL}

RUN npm run build

FROM nginx:stable-alpine

# The nginx image renders files in /etc/nginx/templates into conf.d when the
# container starts, replacing ${COLOUR} and ${APP_VERSION}. The filter makes
# sure no other nginx variable (like $host) is touched. The defaults keep
# staging working, where these variables are not set.
ENV COLOUR=none \
    APP_VERSION=dev \
    NGINX_ENVSUBST_FILTER="COLOUR|APP_VERSION"

COPY nginx.conf /etc/nginx/templates/default.conf.template

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]