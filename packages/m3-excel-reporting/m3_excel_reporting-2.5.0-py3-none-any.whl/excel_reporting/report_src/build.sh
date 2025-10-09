#!/bin/sh

javac -classpath ../report_lib/poi-3.7-20101029.jar:../report_lib/poi-ooxml-3.7-20101029.jar:../report_lib/json_simple-1.1.jar Report.java

jar cfme ../report.jar manifest.mf Report *.class

rm *.class
