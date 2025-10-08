#!/bin/bash
nohup java -Djava.net.preferIPv4Stack=true -Djava.net.preferIPv6Addresses=false --enable-native-access=ALL-UNNAMED -jar ./qis.jar &
