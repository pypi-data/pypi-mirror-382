@echo off
start /b java -Djava.net.preferIPv4Stack=true -Djava.net.preferIPv6Addresses=false --enable-native-access=ALL-UNNAMED -Djava.awt.headless=true -jar qis.jar

