sed -i "s/'{SECRET_DB_HOST}'/'delphi_database_epidata'/g" ../secrets.py
sed -i "s/('{SECRET_DB_USERNAME_EPI}', '{SECRET_DB_PASSWORD_EPI}')/('user', 'pass')/g" ../secrets.py
printf "\n# Copy test files\nCOPY common_full common_full\n" >> ../../dev/docker/python/Dockerfile