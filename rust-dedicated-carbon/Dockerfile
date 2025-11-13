FROM docker.io/cm2network/steamcmd:latest

LABEL org.opencontainers.image.source=https://github.com/herheliuk/rust-game-server
LABEL org.opencontainers.image.authors="Andrii Herheliuk <andrii@herheliuk.com>"
LABEL org.opencontainers.image.licenses=MIT

RUN mkdir -p /home/steam/rustserver/server/

WORKDIR /home/steam/rustserver/

RUN curl -L https://github.com/CarbonCommunity/Carbon/releases/download/production_build/Carbon.Linux.Release.tar.gz \
    | tar -xz

COPY --chown=steam:steam ./entrypoint.sh ./

RUN chmod +x ./entrypoint.sh ./carbon.sh

EXPOSE 28015 28017 28082

ENTRYPOINT ["./entrypoint.sh"]
