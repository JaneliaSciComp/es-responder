#!/bin/bash
if [ $# -eq 0 ]; then
  PROJECT=`pwd | awk -F"/" '{print $NF}'`
  VERSION=1.0.0
elif [ $# -eq 1 ]; then
  PROJECT=$1
  VERSION=1.0.0
else
  PROJECT=$1
  VERSION=$2
fi
VERSIONED=`echo $PROJECT:$VERSION`
read -p "Do you want to build and push $VERSIONED? " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1 # handle exits from shell or function but don't exit interactive shell
fi
oc project ${PROJECT}
oc start-build ${PROJECT} --from-dir=api  -n ${PROJECT} --follow
oc tag ${PROJECT}/${PROJECT}:latest ${PROJECT}/${PROJECT}:${VERSION} -n ${PROJECT}
oc set image deployment/${PROJECT} app=image-registry.openshift-image-registry.svc:5000/${PROJECT}/${PROJECT}:${VERSION} -n ${PROJECT}
