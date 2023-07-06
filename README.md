<div align="center">

# ◐ &nbsp; GPT-Migrate &nbsp; ◑

**Easily migrate your codebase from one framework or language to another.**

<p>
<a href="https://github.com/0xpayne/gpt-migrate/commits"><img alt="GitHub Last Commit" src="https://img.shields.io/github/last-commit/0xpayne/gpt-migrate" /></a>
<a href="https://github.com/0xpayne/gpt-migrate/issues"><img alt="GitHub Issues" src="https://img.shields.io/github/issues/0xpayne/gpt-migrate" /></a>
<a href="https://github.com/0xpayne/gpt-migrate/pulls"><img alt="GitHub Pull Requests" src="https://img.shields.io/github/issues-pr/0xpayne/gpt-migrate" /></a>
<a href="https://github.com/0xpayne/gpt-migrate/blob/main/LICENSE"><img alt="Github License" src="https://img.shields.io/badge/License-MIT-green.svg" /></a>
<a href="https://github.com/0xpayne/gpt-migrate"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/0xpayne/gpt-migrate?style=social" /></a>
</p>

<br />

</div>

Today only - please share some love on [Product Hunt](https://www.producthunt.com/posts/gpt-migrate)! 🚀

If you've ever faced the pain of migrating a codebase to a new framework or language, this project is for you. 

https://user-images.githubusercontent.com/25165841/250232917-bcc99ce8-99b7-4e3d-a653-f89e163ed825.mp4

Migration is a costly, tedious, and non-trivial problem. Do not trust the current version blindly and please use responsibly. Please also be aware that costs can add up quickly as GPT-Migrate is designed to write (and potentially re-write) the entirety of a codebase.

However, with the collective brilliance of the OSS community and the current state of LLMs, it is also a very tractable problem.

## ⚡️ Usage

1. Install Docker and ensure that it's running. It's also recommended that you use at least GPT-4, preferably GPT-4-32k.

2. Set your [OpenAI API key](https://platform.openai.com/account/api-keys) and install the python requirements:

`export OPENAI_API_KEY=<your key>`

`pip install -r requirements.txt`

3. Run the main script with the target language you want to migrate to:

`python main.py --targetlang nodejs`

4. (Optional) If you'd like GPT-Migrate to validate the unit tests it creates against your app before it tests the migrated app with them, please have your existing app exposed and use the `--sourceport` flag. For executing this against the benchmark, open a separate terminal, navigate to the `benchmarks/language-pair/source` directory, and run `python app.py` after installing the requirements. It will expose on port 5000. Use this with the `--sourceport` flag.

By default, this script will execute the flask-nodejs benchmark. You can specify the language, source directory, and many other things using the options guide below.

## 💡 Options

You can customize the behavior of GPT-Migrate by passing the following options to the `main.py` script:

- `--model`: The Large Language Model to be used. Default is `"gpt-4-32k"`.

- `--temperature`: Temperature setting for the AI model. Default is `0`.

- `--sourcedir`: Source directory containing the code to be migrated. Default is `"../benchmarks/flask-nodejs/source"`.

- `--sourcelang`: Source language or framework of the code to be migrated. No default value.

- `--sourceentry`: Entrypoint filename relative to the source directory. For instance, this could be an `app.py` or `main.py` file for Python. Default is `"app.py"`.

- `--targetdir`: Directory where the migrated code will live. Default is `"../benchmarks/flask-nodejs/target"`.

- `--targetlang`: Target language or framework for migration. Default is `"nodejs"`.

- `--operating_system`: Operating system for the Dockerfile. Common options are `'linux'` or `'windows'`. Default is `'linux'`.

- `--testfiles`: Comma-separated list of files that have functions to be tested. For instance, this could be an `app.py` or `main.py` file for a Python app where your REST endpoints are. Include the full relative path. Default is `"app.py"`.

- `--sourceport`: (Optional) Port for testing the unit tests file against the original app. No default value. If not included, GPT-Migrate will not attempt to test the unit tests against your original app.

- `--targetport`: Port for testing the unit tests file against the migrated app. Default is `8080`.

- `--guidelines`: Stylistic or small functional guidelines that you'd like to be followed during the migration. For instance, "Use tabs, not spaces". Default is an empty string.

- `--step`: Step to run. Options are `'setup'`, `'migrate'`, `'test'`, `'all'`. Default is `'all'`.

For example, to migrate a Python codebase to Node.js, you might run:

```bash
python main.py --sourcedir /path/to/my-python-app --sourceentry app.py --targetdir /path/to/my-nodejs-app --targetlang nodejs
```

This will take the Python code in `./my-python-app`, migrate it to Node.js, and write the resulting code to `./my-nodejs-app`.

#### GPT-assisted debugging
https://user-images.githubusercontent.com/25165841/250233075-eff1a535-f40e-42e4-914c-042c69ba9195.mp4

## 🤖 How it Works

For migrating a repo from `--sourcelang` to `--targetlang`...

1. GPT-Migrate first creates a Docker environment for `--targetlang`, which is either passed in or assessed automatically by GPT-Migrate.
2. It evaluates your existing code recursively to identify 3rd-party `--sourcelang` dependencies and selects corresponding `--targetlang` dependencies.
3. It recursively rebuilds new `--targetlang` code from your existing code starting from your designated `--sourceentry` file. This step can be started from with the `--step migrate` option.
4. It spins up the Docker environment with the new codebase, exposing it on `--targetport` and iteratively debugging as needed.
5. It develops unit tests using Python's unittest framework, and optionally tests these against your existing app if it's running and exposed on `--sourceport`, iteratively debugging as needed. This step can be started from with the `--step test` option.
6. It tests the new code on `--targetport` against these unit tests.
7. It iteratively debugs the code for for you with context from logs, error messages, relevant files, and directory structure. It does so by choosing one or more actions (move, create, or edit files) then executing them. If it wants to execute any sort of shell script (moving files around), it will first ask for clearance. Finally, if at any point it gets stuck or the user ends the debugging loop, it will output directions for the user to follow to move to the next step of the migration.
8. The new codebase is completed and exists in `--targetdir`.

### 📝 Prompt Design

Subprompts are organized in the following fashion:

- `HIERARCHY`: this defines the notion of preferences. There are 4 levels of preference, and each level prioritized more highly than the previous one.
- `p1`: Preference Level 1. These are the most general prompts, and consist of broad guidelines.
- `p2`: Preference Level 2. These are more specific prompts, and consist of guidelines for certain types of actions (e.g., best practices and philosophies for writing code).
- `p3`: Preference Level 3. These are even more specific prompts, and consist of directions for specific actions (e.g., creating a certain file, debugging, writing tests).
- `p4`: Preference Level 4. These are the most specific prompts, and consist of formatting for output.

Prompts are a combination of subprompts. This concept of tagging and composability can be extended to other properties as well to make prompts even more robust. This is an area we're highly interested in actively exploring.

In this repo, the `prompt_constructor()` function takes in one or more subprompts and yields a string which may be formatted with variables, for example with `GUIDELINES` being a `p1`, `WRITE_CODE` being a `p2` etc:

```python
prompt = prompt_constructor(HIERARCHY, GUIDELINES, WRITE_CODE, DEBUG_TESTFILE, SINGLEFILE).format(targetlang=targetlang,buggyfile=buggyfile)
```

## 📈 Performance

GPT-Migrate is currently in development alpha and is not yet ready for production use. For instance, on the relatively simple benchmarks, it gets through "easy" languages like python or javascript without a hitch ~50% of the time, and cannot get through more complex languages like C++ or Rust without some human assistance.

## ✅ Benchmarks

We're actively looking to build up a robust benchmark repository. If you have a codebase that you'd like to contribute, please open a PR! The current benchmarks were built from scratch: REST API apps which have a few endpoints and dependency files.

## 🧗 Roadmap

Below are improvements on the to-do list. If you'd like to knock any of these or others out, please submit a PR :)

#### High urgency
- Add logic for model input size limiting based on the window size. See issue [#2](https://github.com/0xpayne/gpt-migrate/issues/2).

#### Med urgency
- Add unit tests to the entire project for better reliability and CI/CD
- Add more benchmark examples, especially larger repos
- Add functionality to let the LLM request access to dependency functions in other files as it debugs
- Add support for other LLMs

#### Low urgency
- Enable internet search requests as the model debugs
- Identify and compile language-specific issues + solve for them

## 📣 Call to Action

We're looking for talented contributors. Whether you have a particular passion about a specific language or framework, want to help in creating a more robust test suite, or generally have interesting ideas on how to make this better, we'd love to have you!

## 🛠 Expert-Assisted Migration

Due to the inflow of requests, we've decided to create a standardized process for helping people with their migrations. If you're a company that needs help with a big migration or an expert that is willing to help with them, please visit the following website: [https://gpt-migrate.com/](https://gpt-migrate.com/)

## Join the conversation on [Twitter](https://twitter.com/joshpxyne/status/1675254164165910528)!