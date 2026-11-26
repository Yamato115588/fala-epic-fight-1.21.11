#!/bin/sh
set -eu
: "${FABRIC_CLASSPATH:?Provide Fabric Loader and Sponge Mixin on the compile classpath}"
mkdir -p build/classes
"$JAVA_HOME/bin/javac" --release 21 -proc:none -cp "$FABRIC_CLASSPATH" -d build/classes src/main/java/th/falasiayacraft/economy/SignShopFieldMixin.java
"$JAVA_HOME/bin/jar" --create --file build/fala-saros-sign-compat-0.1.0-dev.1.jar -C build/classes . -C src/main/resources .
