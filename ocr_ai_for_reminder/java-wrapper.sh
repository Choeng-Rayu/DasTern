#!/bin/bash
# This script redirects to Java 21 if available, otherwise Java 25
# It's used to work around Gradle compatibility issues with Java 25

if [ -x "/usr/lib/jvm/java-21-openjdk/bin/java" ]; then
    exec "/usr/lib/jvm/java-21-openjdk/bin/java" "$@"
else
    # Fall back to system Java
    exec /usr/bin/java "$@"
fi
