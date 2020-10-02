# start with a standard php7+apache image
FROM php:7-apache

# use PHP's recommended configuration
RUN mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

# install and enable PHP's `mysqli` extension
RUN docker-php-ext-install mysqli
RUN docker-php-ext-enable mysqli

# use delphi's timezome
RUN ln -s -f /usr/share/zoneinfo/America/New_York /etc/localtime
RUN sed -i $PHP_INI_DIR/php.ini -e 's/^;date.timezone =$/date.timezone = "America\/New_York"/'

# deploy development secrets (see `operations/deploy.json`)
COPY repos/delphi/operations/dev/docker/web/assets/secrets.php /var/www/html/
RUN chmod o+r /var/www/html/secrets.php
