#!/usr/bin/env bash
# Updates the third party libraries and their dependencies
# Needs pip installed, and is a Linux-only script
# This should be run from within the Tools directory of cadquery-freecad-module

# Set up a temporary directory for downoading and extracting
if [ -d "temp" ]; then
  rm -rf temp/
fi
mkdir temp/
cd temp/

# Grab all cqparts packages
pip search cqparts- | awk '{print $1}' | xargs -L1 pip download

# Removing these allows us to stick with our already installed versions
rm pyparsing*
rm cadquery*

# Put the required libs in the proper place
ls *.whl | grep -v cqparts | xargs -L1 unzip
ls *.whl | grep -v cqparts | tr '[:upper:]' '[:lower:]' | awk -F "-" '{print $1}' | xargs -I {} cp -R {} ../../Libs/

# Clean up any libraries that were just single files
deps=`ls *.whl | grep -v cqparts | tr '[:upper:]' '[:lower:]' | awk -F "-" '{print $1}'`
for dep in $deps; do
  cp "${dep}.py" ../../Libs/
done

# Extract all the relevant components of cqparts to the ThirdParty directory
ls *.whl | grep cqparts | xargs -L1 unzip
ls *.whl | grep cqparts | awk -F "-" '{print $1}' | xargs -I {} cp -R {} ../../ThirdParty/

# Clean up temporary files
cd ../
rm -rf temp/
