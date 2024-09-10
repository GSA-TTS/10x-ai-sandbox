ARG base
FROM ${base}

ARG packages
ARG package_args='--allow-downgrades --allow-remove-essential --allow-change-held-packages --no-install-recommends'

RUN  apt-get -y $package_args update && \
  apt-get -y $package_args install $packages && \
  apt-get clean && \
  find /usr/share/doc/*/* ! -name copyright | xargs rm -rf

EXPOSE 8080

COPY . .

CMD ["npm", "..."] 