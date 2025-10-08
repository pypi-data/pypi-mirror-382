
#Install Wheel
```shell
pip install wheel
```

#Install this Package
```shell
pip install .
```
Use this command when inside this (INSTALL.md) folder extracted.

#Install in conda
```shell
conda activate env_name
conda install pip
pip install .
```


#Custom bash script
We need to launch with additional parameters when launching the logical server.
*WARNING: Doing so may cause incompatibility with Sapio platform's script engine.*

Prepend the script with anaconda environment activation, if necessary.
```shell
java -Dpython.console.encoding="UTF-8" \
-Dpython.security.respectJavaAccessibility="false" \
-Dpython.import.site=false \
-Dcom.sun.management.jmxremote=true -Dcom.sun.management.jmxremote.port=8694 -Dcom.sun.management.jmxremote.local.only=false -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false -Djava.net.preferIPv4Stack=true -Xmx4096M -Xms256M -Xdebug -Xrunjdwp:transport=dt_socket,address=*:5000,server=y,suspend=n -Djava.net.debug=ssl -Dtrust_all_cert=true -classpath veloxserver.jar:lib/serverdependencies.jar com.velox.server.datamgmtserver.DataMgmtServerImpl
```

#Custom bash script using conda3
Note that the conda shell script is local to the exemplar user after install.

*It is important to grant the conda.sh file "Read" and "Execute" permission on the user running the script*.
```shell
source ~/anaconda3/etc/profile.d/conda.sh
eval $(conda shell.bash hook)
conda activate env_name
/usr/lib/jvm/java-11-openjdk-amd64/bin/java \
-Dpython.console.encoding="UTF-8" \
-Dpython.security.respectJavaAccessibility="false" \
-Dpython.import.site=false \
-Dcom.sun.management.jmxremote=true \
-Dcom.sun.management.jmxremote.port=4457 \
-Dcom.sun.management.jmxremote.local.only=false \
-Dcom.sun.management.jmxremote.ssl=false \
-Dcom.sun.management.jmxremote.authenticate=false \
-Djava.rmi.server.hostname=ironman \
-Djava.net.preferIPv4Stack=true \
-agentpath:/opt/jprofiler11/bin/linux-x64/libjprofilerti.so=port=8849,nowait \
-Xmx24G \
-Xms256M \
-XX:+UseG1GC \
-XX:MaxHeapFreeRatio=50 \
-Xdebug \
-Xrunjdwp:transport=dt_socket,address=*:5017,server=y,suspend=n \
-classpath veloxserver.jar:lib/serverdependencies.jar \
com.velox.server.datamgmtserver.DataMgmtServerImpl
```