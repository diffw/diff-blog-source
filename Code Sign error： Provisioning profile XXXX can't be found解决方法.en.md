---
title: 'How to Resolve ''Code Sign Error: Provisioning Profile XXXX Can''t Be Found'''
date: 2011-11-21 08:29:39+00:00
draft: false
tags:
- ios
translationKey: how-to-resolve-code-sign-error-provisioning-profile
slug: how-to-resolve-code-sign-error-provisioning-profile
source_hash: 2db7bcde5e698e3c814cf6f5784d8f4c63b771852b3ac49ca86e614f02a287ef
---

Recently, while testing an app on a physical device using Xcode, I added a new device, requiring an update to the provisioning profile. I deleted the old profile, downloaded a new one, and installed it, only to encounter the error:

Code Sign error: Provisioning profile XXXX can't be found

I found a [method](http://www.cnblogs.com/baryon/archive/2010/05/06/1728968.html) via Google, but the download speed for the text editor was frustratingly slow. So, I figured out my own solution, and it worked as follows:

Go to the project, under Build Settings, click on the code signing identity option. Select "other..." and change the old provisioning identifier (a string of numbers) in the edit box to the new one.

Note: You can find the provisioning identifier in the organizer.
