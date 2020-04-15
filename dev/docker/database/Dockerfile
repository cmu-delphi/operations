# start with a standard mariadb image
FROM mariadb

# use delphi's timezome
RUN ln -s -f /usr/share/zoneinfo/America/New_York /etc/localtime

# specify a development-only password for the database user "root"
ENV MYSQL_ROOT_PASSWORD pass
