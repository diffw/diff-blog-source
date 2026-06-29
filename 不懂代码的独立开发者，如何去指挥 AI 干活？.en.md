---
title: How Non-Coding Indie Developers Can Direct AI to Work
date: 2026-06-29 16:48:11-05:00
draft: false
tags:
- ai
- design
slug: how-non-coding-indie-developers-direct-ai
source_hash: d5c8b078af1dc25cb31047798dc9f4ec7246cfc165cd7e38cb427e3ecdce27a3
---

As an indie developer who doesn't understand development or coding, I have a few tips to share for working with AI.

If you've been a boss or manager and have led a business team before, your background will be helpful in communicating with AI. Often, bosses and managers don't know technical details — so how do they communicate with tech people?

The key is: **Convey clear intent, understand the implementation process, define the final acceptance criteria, and manage key data.**

Use the same approach with AI. I think it comes down to the following steps.

## 1. Explain User-Driven Needs

When working with AI, start from the user's perspective. Be clear about your intentions and needs, and try to describe them objectively.

For example, don't just say, "Help me make a login page." 

Say, "I want users to log in with their email when they open the page; if they enter it wrong, they should see an error message; if it's on a phone screen, the button and input box shouldn't be squished together."

Not knowing code is okay, but **you need to understand how users will use it.**

## 2. Have AI Paraphrase

Make sure AI repeats back its understanding of your intent. This is also a small management trick: when assigning tasks, make sure your subordinates or team members repeat your intention to avoid misunderstandings.

I've often said when working with leaders: "Did you mean this? Am I understanding you correctly?"

That's an alignment process.

## 3. Let AI Interview You

Often, we can't explain our needs clearly from the start. Especially if you don't know code, it's easy to describe a vague idea without realizing what details affect development.

This is when you can reverse the process and let AI interview you.

For instance, say: "Ask me questions like a product manager and engineer until you understand enough about the feature. Then help me organize it into development specs."

The advantage here is that **you don't need to write a perfect prompt right away.** Just answer questions, letting AI gradually turn vague ideas into clear requirements.

## 4. Align Using ASCII, Flowcharts, and Screenshots

I've mentioned this many times: using ASCII is a great, low-cost, fast way to align needs and ideas.

But it doesn't just have to be ASCII. Flowcharts, page screenshots, design drafts, and error screenshots can all help align you and AI.

For those who don't know code, **screenshots are often more accurate than describing it in a hundred words.**

For example, what I'm doing with VibeCap revolves around this scenario: quickly screenshotting and annotating on macOS, then pasting directly into AI tools like ChatGPT, Claude, or Cursor. It isn't a complex development tool, but it solves a very real problem: how to quickly show AI what you're seeing in an interface, error, or detail.

![VibeCap homepage screenshot](https://vibecap.dev/hero-screenshot.png)

For non-technical indie developers, this screenshot capability is crucial. You may not be able to describe where the code breaks, but you can show AI "what looks wrong."

## 5. Set Clear Completion Criteria for AI

**Don't just give AI a task; also tell it what completion looks like.**

For instance, you might say, "When this feature is done, it needs to meet these conditions: the page can open, buttons are clickable, error states show prompts, and it doesn't deform on a phone."

This is very similar to managing a team. You can't just say "get this done well" — you have to explain "what qualifies as well."

With AI, the clearer you can be about completion criteria, the less likely it is to go off track on its own.

## 6. Build a Minimal Viable Version First

Don't start by having AI build a complete product.

A better method is to first build a minimal version — something that opens, is clickable, and shows a basic flow. Once this version runs, you can layer in functions, styles, and details.

This is especially important for those who don't know code. If you start by having AI handle login, payment, database, UI, backend, and permissions all at once, you won't know which part broke when something goes wrong.

**Let it start small, run a little, then continue step by step.**

## 7. Fix One Issue at a Time

When you see several issues, it's easy to dump them all on AI in one go: "This is wrong, that's also wrong, plus optimize this."

But in my experience, this easily leads to a mess.

A more stable way is **to fix one issue at a time.** For example, first fix the misaligned button on the phone, confirm it, then fix the text style; confirm that, then adjust the interaction logic.

This isn't inefficient; it's reducing the chance of chaos.

## 8. Intervene and Stop Timely

Let AI break out of its routine. For instance, if a task runs for two to five hours without effect, I'll stop AI and give it some prompt keywords.

For example, using First Principle or Critical Thinking can help it reframe and deconstruct tasks, finding the fundamental elements and verifying from the basics.

Throwing out these keywords can work wonders.

Of course, I've also gradually realized it's best not to wait four or five hours before intervening. A better method is **to set a boundary early:** if something can’t be fixed after two attempts, or the same issue repeats, stop and have AI recast the problem, break down causes, then proceed.

## 9. Have AI Research and Reference Mature Solutions

When having AI develop a solution, let it first conduct academic and industry research, or refer to active and well-maintained related projects on GitHub.

But here, I think you need to be a bit careful: being top-ranked or highly starred doesn't necessarily mean it's right for your project. Have AI casually check a few things like if the project is actively maintained, if the license is suitable, if issues are left unaddressed, if there are tests, and if it's compatible with your current stack.

I've found that AI sometimes easily gets lazy, or it tends to go about some so-called innovation. But for the level of difficulty in my current project, there's no need for AI to innovate too much. The existing resources and open-source projects are more than enough for my use.

So for indie developers who don’t understand code, **the important part isn't learning to code, but learning to direct AI like a clear manager:** articulate goals, provide sufficient context, break into small steps, define completion standards, and pull it back if it strays.  
