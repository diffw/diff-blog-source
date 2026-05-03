---
title: 'Fix for Code Sign Error: Provisioning Profile XXXX Can''t Be Found'
date: 2011-11-21 08:29:39+00:00
draft: false
tags:
- ios
translationKey: fix-code-sign-error-provisioning-profile-cant-be-found
slug: fix-code-sign-error-provisioning-profile-cant-be-found
source_hash: 2db7bcde5e698e3c814cf6f5784d8f4c63b771852b3ac49ca86e614f02a287ef
---

Recently, while testing an app on a device via Xcode, I needed to update the provisioning because I added a new device. I deleted the old provisioning, downloaded a new one, installed it, and then got this error:
Code Sign error: Provisioning profile XXXX can't be found
I found a [solution](http://www.cnblogs.com/baryon/archive/2010/05/06/1728968.html) on Google, but downloading the text editor was too slow for me, so I found another method that works:
Go to the project, Build Settings, click on the code signing identity option, select "other...", and change the old provisioning identifier (a string of numbers) in the edit box to the new one.
Note: You can find the provisioning identifier in the organizer.
