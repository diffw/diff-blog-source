---
title: How I Use AI to Assist My Writing
date: 2026-05-04 10:05:00-06:00
draft: false
tags:
- ai
slug: how-i-use-ai-to-assist-my-writing
source_hash: 92cfe2c30c66f5b04a19aeeca960caacc358df403253e86be0bbc63e664b6b0a
---

I'm a designer by profession, and I've had formal art training, so I've always been a visually-oriented thinker. But strangely, I seem to prefer words over images. Though I was practically tortured writing diaries as a kid, by the time I got to college, especially around 2001 when blogging was just beginning, I really loved it. Writing on the internet and sharing my thoughts.

From 2001 to now, twenty-five years — I haven't stopped.

Just a side note, I really dislike the term 'little essays.' To me, it feels like an insult to writing.

I don't just accept using AI tools for writing; I love using AI. But I really can't stand using AI to generate articles directly, especially if it's something I don't even want to read or review before handing it off. That's something I can't tolerate.

So, I have some baseline principles for AI-assisted writing:

1. The core ideas or concepts have to be yours, not AI-generated. Otherwise, it feels pointless.
2. The basic structure and framework of the article, the 'meat' of it, should be produced by you, not by AI.
3. I want my writing style and the final format to show no signs of AI. If you have a specific writing style, using AI shouldn't change that.

In short, AI should assist or help you in writing, not replace you.

Here are some of my experiences and methods for using AI tools in writing.

### I Keep a List of Article Ideas

Like other professional work, one of the biggest challenges in writing is not knowing what to write, especially when you're suddenly asked to write something and have no ideas.

I'm actually someone with a lot of ideas, but I still encounter times when inspiration doesn't come. So, more than a decade ago, I developed a habit: if I have an idea, I jot it down. Sometimes it's a title, or other times a core idea. This way, I can maintain a list of articles I want to write.

### I Use Voice Input

Some say typing is inhumane, and I completely agree. About two or three years ago, I started using WeChat's voice-to-text feature for input.

Now, I use a tool called Typeless, which is really handy. After the trial period ended, I felt like I lost a crucial tool, so I went ahead and bought a one-year membership.

I use voice input to quickly draft a basic outline, then write out each section by voice.

### I Have a Custom AI Editing Process

This is a core part of my AI usage: how to get AI to modify and polish my original input without changing my intended meaning.

At first, I would create a project in ChatGPT specifically for editing, writing prompts and instructions with simple constraints.

For example:
1. Don't change my original meaning.
2. Only correct typos.
3. Fix grammar mistakes and connections.

But these edits were limited. Later, using Cursor and Claude Code, I started using Rules and Skills.

Rules and Skills themselves don't need to be written by me.

I have AI set these Rules and Skills based on its best understanding. But I provided a critical resource: I let the AI read almost 300 of my past blogs, articles, and diaries to summarize my writing style, strengths, and 'quirks' that aren't really flaws.

I hope AI can manage two things when editing:

Basic Corrections: Address basic writing issues like typos and fluency.

Style Alignment: The edited content should match my past language habits and writing style, even intentionally retaining some of my 'quirks.'

Finally, I bundled these into a comprehensive set of Rules and Skills.

Every time, all I need to do is throw the voice input draft into the editor as an MD document.

At that point, the AI runs the Skills according to the rules, giving me an edited piece that often meets my expectations so well I don't need to scrutinize what it changed.

### I Have an Automated Publishing Process

Currently, I use Obsidian to write and publish. To be honest, I'm not a big fan of Obsidian because it's complicated; I prefer simpler, more straightforward products like Bear Note.

But I chose Obsidian for several reasons:
1. It's free (Bear Note costs about 128 RMB a year).
2. Although free, it supports iCloud automatic sync. Just place your articles' directory in iCloud, and your articles can sync automatically between MacBook and iPhone.
3. Obsidian supports Git commands, so I can execute some Git operations like publishing.

After writing an article, I'd do a Git Push in Obsidian, then the article gets published onto my official blog.

I can also copy the article from the Obsidian directory on my phone or computer and post it on platforms like Xiaohongshu or on my WeChat newsletter.

### I Have an Automated English Translation Process

Since I'm based in the US, and I'll eventually involve other languages in my indie software development, I also need English content.

I set up an automated translation Rules and Skills in Claude Code. When I write a Chinese article and hit Git Push in Obsidian, the system calls OpenAI's API remotely, automatically translating it into English, and then posts it to my Blog.

But this workflow currently only publishes to the Blog, not platforms like Xiaohongshu or WeChat.

This translation Skill is quite interesting. First, it translates based on my finalized Chinese draft; secondly, it adapts to native language habits; plus, my articles cover a wide range including life, technology, investment, and faith, so I want it to maintain a level of professionalism across these fields, with specialized terminology suitable for each industry.

I also let it review many of my past articles to understand my background. For instance, since I'm from China, when the text refers to 'domestically,' it needs to understand that 'domestically' means mainland China. With such info, its translation sticks as close to my background as possible.

Of course, it can keep improving and iterating.

### Things I'm Planning to Try Next

Every day, I have a lot of ideas and content fragments, but organizing them takes time. I want to freely express my ideas and have AI help organize them. Once there's a degree of completion, AI could directly turn them into articles, or social media snippets, and publish them.

AI can help determine which article fits which platform. For example, psychology articles on Xiaohongshu are likely throttled.

I plan to run my Twitter account, so I'm considering this: AI can define an optimal social platform operation growth role for me, setting certain content standards. The specific steps are:

1. Regularly extract suitable content from all my past records (whether fully formed articles or scattered ideas).
2. Organize content on a timeline (like today, this week, this month) for Twitter posts.
3. I just need to click one button to publish, maybe even automate publication.

Though, as far as I understand, Twitter's publishing API is paid. That's an expense I'll have to factor in.
