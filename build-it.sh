#!/bin/sh

pdebuild --debbuildopts "-I.svn -I.empty -I*.pyc -I.zim*" --logfile ../build.log

sudo dpkg -i /var/cache/pbuilder/result/xetex-tipe_0.2-2.3_all.deb /var/cache/pbuilder/result/xetex-tipe-examples_0.2-2.3_all.deb
