---
title: Demo
author: John Doe
date: 2026-01-24
---

This is a normal markdown document `(・_・ヾ`.

However, when rendered using pandoc with the provided templates, it has some perks!

# What is tern?

Tern is a modular batch conversion interface.

In other words, it frees you from the ass pain of running `pandoc -f markdown --template='docs.html' --mathjax --embed-resources --css="$PANDOC_DOCS_CSS" -t html -i <input.md> -o <output.html>` for every documentation file in your repository.

It uses some Lua magick, but don't worry about it, the Nix devshell takes care of that!

<details>
<summary>How to get Nix and activate the devshell?</summary>

1.  Follow installation instructions from official Nix wiki: <https://nix.dev/install-nix.html>

    > Supported platforms: Linux, MacOS, WSL2, Docker

1.  Activate devshell.

    ```bash
    nix-develop # Run this on project's root (i.e. in the same directory where .git resides)
    ```

</details>

## How to use tern?

It has some crappy UI made with Slint; don't worry tho, it'll be replaced with a better one made in SDL3 eventually.

Never mind that, the rest is dope, since it's set and forget.

1.  Select an engine, source and output path, etc

    > I've already done this, ignore this step - Steven

    ```bash
    tern
    ```

    A window should pop up, fill out the "form"

1.  Convert files

    ```bash
    tern
    ```

## Any tip?

Yeah, since `tern` tracks file metadata to not re-render up-to-date files. You can trick it into re-rendering some file by updating metadata, the simplest way to do it in Linux is with the following command: `touch <file>`

You can also run tern with the force option which will re-render all documents: `tern -f`

## More options?

You can always check them with: `tern --help`

# Miscellaneous

## How to view documentation?

You can serve it using a simple HTTP Python server:

```bash
python -m http.server -d docs 8080 # This works in Python 3.7 and onwards
```

Then open up in your browser: <http://localhost:8080>

## Any problem, bug?

Tell me about it, I'll fix it - Steven

# About the templates {.tabset}

As you saw before, you can add collapsable/expandable sections with a `<details>` HTML block.

You can also add tabs by annotating a section header with `{.tabset}`, then, its subheaders become tabs.

## Tab 1

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

## Tab 2

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.

Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur?
