tl;dc
================

## about

This is a work in progress and it'll likely stay that way for a while. It's just another agentic AI CLI tool, with a focus on xAI's response API. Support for stateless APIs is also possible, as evidenced by Ollama support - that one is borked for now though, see below.

## status / roadmap

* xAI/Grok works fine.
* Ollama does not work fine, tool calling is borked, so it's useless for now.
* For now, only 3 tools are available to the AI: listing files, reading a file, writing a file. AI **cannot** leave current directory and **cannot** execute shell commands. This is by design.

## manual

* xAI configuration:
```bash
tldc models add grok-code-fast-1 xai '{"api_key": "<API_KEY>"}'
tldc models set grok-code-fast-1
```
* For the list of available commands, just run `tldc` without parameters.
* Active model is a global setting.
* Context refers to the current working directory. It stores things like message history, last response ID, as well as synchronization status and checksums for all the files.
* _All the files_ above means all the files listed as available to the AI. Some things are excluded, see `constants.py`.

## too lazy; didn't code
_aka what's with the name_

The best way to code is as follows:
* plan what needs to be done
* tell someone else to do it
* grab a coffee
* code review
* profit

You may think that _someone else_ is a bottleneck.
You may think _I'll better do it myself_.
But when it comes to AI, even if it's not as good as you, it **is** faster.

**Orders of magnitude faster**.

So even if you have to repeat those steps several times to get the end result you're after, you're still saving a lot of ~~time~~ money.

And everyone likes money.