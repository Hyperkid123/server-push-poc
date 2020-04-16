#!/bin/bash
gnome-terminal -- kafka/bin/zookeeper-server-start.sh kafka/config/zookeeper.properties
gnome-terminal -- kafka/bin/kafka-server-start.sh kafka/config/server.properties