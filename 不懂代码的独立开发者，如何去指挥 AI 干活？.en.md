---
title: 'Directing AI When You Can''t Code: A Guide for Indie Developers'
date: 2026-06-29 16:48:11-05:00
draft: false
tags:
- ai
- design
slug: directing-ai-for-indie-devs
source_hash: 1a6c463e27f694c9be4a9b60537ff951b825d1811c01e5c2859dea1b4584273b
---

As an indie developer who doesn't understand coding, I've got a few tips for communicating with AI.

If you've been a boss or manager, or led a business team before, that background can really help when talking to AI. Often, bosses and managers don't know tech. So how do you communicate with tech folks?

The key is: **you need to express clear intent, understand the process, be clear about the final acceptance criteria, and grasp key data.**

You can apply the same approach with AI. I think the process can be broken down into a few steps:

## 1. Clearly State User-Centered Needs

When working with AI, start from the user's perspective. Clearly express your intent and needs, and describe them as objectively as possible.

For example, don't just say: "Help me make a login page."

You could say: "I want users to be able to log in with an email when they open the page; if they input wrong info, show an error; on a phone screen, ensure buttons and input fields aren't squished."

Not knowing code is fine, but **you must understand how users will use it.**

## 2. Have AI Repeat Back to You

Make AI repeat its understanding of your intent. This is a trick in management too: when giving tasks, to prevent misunderstandings, have your subordinate or team member repeat back your intent.

Like when I work with leaders, I'll often say: "Boss, is this what you meant? Did I get it right?"

It's a process of alignment.

## 3. Let AI Interview You

Often, we can't articulate the needs clearly from the start. Especially for those who don't understand code, it's easy to describe a vague idea without knowing which details affect development.

At this point, let AI interview you.

You might say: "Pretend you're a product manager and engineer—ask me questions. Once you understand the feature well, help me draft the development notes."

This approach means **you don't need to write a perfect prompt at first.** Just answer the questions so AI can help organize your vague thoughts into clear needs.

## 4. Use ASCII, Flowcharts, and Screenshots to Align

I've mentioned this many times before: using ASCII is a great, low-cost way to quickly align on needs and ideas.

But it's not just ASCII. Flowcharts, page screenshots, design draft screenshots, error screenshots—they can all help you align with AI.

Especially for non-coders, **a screenshot is often more accurate than a hundred words.**

For example, with VibeCap, the scenario is about quickly taking screenshots, annotating, and pasting them into tools like ChatGPT, Claude, Cursor on macOS. It's not a complex development tool, but it solves a real problem: quickly passing along what you see, errors, details, to AI.

![VibeCap Home Screenshot](https://vibecap.dev/hero-screenshot.png)

For non-tech indie developers, this screenshot capability is important. You might not describe why the code is wrong, but you can highlight "what doesn't look right" to AI.

## 5. Provide AI with a Clear Completion Standard

**Don't just give AI a task—tell it what completion looks like.**

For instance, you could say: "Once this feature is done, it needs to meet these conditions: the page opens, buttons click, error states show hints, no deformation on mobile."

This is very much like managing a team: don't just say, "Make it good," say "what's considered good."

Same goes for AI. The clearer your criteria, the less likely AI will lose its way.

## 6. Build the Smallest Runnable Version First

Don't start with AI building a whole product.

Better to make a minimal version first that opens, clicks, and shows the basic flow. Once that's running, then layer on features, styles, and details.

This is crucial for those who don't know code. If you have AI manage login, payment, databases, UI, backend, and permissions all at once and something breaks, you won't know where the problem is.

**Have it make something small first, run it through, then move to the next step.**

## 7. Fix One Issue at a Time

When you see multiple issues, it's easy to throw them all at AI: "This is wrong, that's wrong, also optimize this."

But in my experience, this can make things messier.

A steadier approach is **fix one problem at a time.** For instance, fix the misalignment on mobile first, confirm it's good, then fix text styles; once confirmed, alter interaction logic.

It's not inefficient; it's reducing chaos.

## 8. Intervene and Stop in Time

Get AI out of its usual pattern. If I've run a task for three, four hours without good results, I stop AI and feed it a prompt with keywords.

Examples: using First Principle or Critical Thinking lets it reframe and deconstruct tasks, identifying basics and verifying from the ground up.

Those keywords actually work wonders.

Of course, I’ve realized it's best not to wait four hours to intervene. A better way is to **set a boundary early**: if it can't fix something twice, or the same issue recurs, stop first, have AI summarize the problem, analyze reasons, then proceed.

## 9. Get AI to Provide Evidence

Another key point: **have AI present evidence.**

AI can be lazy, offering guess-filled answers. When pinpointing issues in AI coding, demand more than "I think maybe this is the issue."

Ask it directly: "From the code perspective, show evidence—what file, segment, logic caused this issue."

Though I may not understand the code, requiring this keeps AI from slacking. At least it takes another step, actually reads code instead of guessing.

For those who don’t code, evidence isn't for reviewing code yourself, it's to **make AI do thorough work first.**

## 10. Make AI Do Research and Reference Mature Solutions

When having AI create a plan, have it research academia and industry, and look at active, well-maintained projects on GitHub.

But a caution: a high rank or many stars doesn't mean a project suits you. Make AI check things like recent updates, license suitability, unresolved issues, testing, compatibility with your tech stack.

AI sometimes takes the easy route or does "innovations"—not always needed for my current project's complexity. Existing resources and open-source projects are often enough for my use.

So for a non-coding indie developer, **the key isn't learning to code, but being a clear manager to direct AI**: articulate goals, give full context, break steps down, define completion standards, and pull things back when AI goes off track.
