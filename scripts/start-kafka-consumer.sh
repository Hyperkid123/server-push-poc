#!/bin/bash
gnome-terminal -- kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test --from-beginning