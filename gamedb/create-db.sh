if [ $# = 0 ]
then
    echo
    echo "Usage: create-db.sh database user password"
    echo
    exit 0
fi
database=$1
user=$2
password=$3
CMD1="CREATE DATABASE IF NOT EXISTS $database;"
CMD2="CREATE USER '$user'@'%' IDENTIFIED BY '$password';"
CMD3="GRANT all privileges on $database.* to '$user'@'%';FLUSH PRIVILEGES;"
echo $CMD1
echo  $CMD1 | mysql -u root

echo $CMD2
echo  $CMD2 | mysql -u root

echo $CMD3
echo  $CMD3 | mysql -u root