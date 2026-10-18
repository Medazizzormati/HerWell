# Build stage
FROM maven:3.8.6-openjdk-17-slim AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests -o target/herwell-backend-1.0.0.jar

# Run stage
FROM openjdk:17-slim
WORKDIR /app
COPY --from=build /app/target/herwell-backend-1.0.0.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
