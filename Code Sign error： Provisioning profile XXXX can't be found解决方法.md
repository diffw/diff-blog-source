---
title: "Code Sign error: Provisioning profile XXXX can't be found解决方法"
date: 2011-11-21T08:29:39+00:00
draft: false
tags: [iOS]
---
最近通过Xcode在真机上测试App，因为新增了device，所以需要更新provision。删除旧的provision，下载新的provision，安装后，报错：
Code Sign error: Provisioning profile XXXX can't be found
google找到一个[方法](http://www.cnblogs.com/baryon/archive/2010/05/06/1728968.html)，但是苦于下载文本编辑器速度太慢，所以，自己找了这个方法，奏效，如下：
去project里面，Build Settings，点击 code signing indentity选项，点“other...”，将编辑框中老的provision identifier（一串编号）改成新的就可以。
注明：provision identifier可以在organizer中找到。
