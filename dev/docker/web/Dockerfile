# start with a standard php7+apache image
FROM php:7-apache

# use PHP's recommended configuration
RUN mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

# install and enable PHP's `mysqli` extension
RUN docker-php-ext-install mysqli
RUN docker-php-ext-enable mysqli

# deploy development secrets (see `operations/deploy.json`)
COPY repos/delphi/operations/dev/docker/web/assets/secrets.php /var/www/html/
