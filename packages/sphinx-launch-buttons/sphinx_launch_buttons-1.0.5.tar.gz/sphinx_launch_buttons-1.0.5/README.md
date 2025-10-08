# Custom launch buttons

## Introduction
The custom launch button extension allows you to create a customizable button in the top right of your jupyter book. 
This may have many applications, one of them being that you can create different language versions of the book available for the user. 

## What does it do?
This extension add a button to the top bar which allows you to link to other website. In combination with a translated book on another branch you can use this to create multilingual books.


## Installation

1. Install the `sphinx-launch-buttons` package using `pip` if you'd like to build your book locally:
```
pip install sphinx-launch-buttons
```

2. Make sure that the package is included in your project's `requirements.txt` to track the dependency:
```
sphinx-launch-buttons
```

3. To use the extension in your book, add the extension to the list of Sphinx extra extensions in your `_config.yml` file, (**important**: underscore, not dash this time):

```yaml
sphinx:
  extra_extensions:
    - sphinx-launch-buttons
```

## Usage
This section will explain how to create a "Languages" button, like you might be used to seeing on just about any website. The use of the button, however, is completely customizable and may be used in many different ways.


1. Include a `_launch_buttons.yml` file in the same location (root directory of your book) as your `_config.yml` file. The following code cell shows the main structure of that file.

```yaml
buttons:
  - type : dropdown

  - type : button
```

Here, `buttons` is an array of launch buttons, each can be identified using 2 types: 'dropdown' or 'button'. The cell above shows 2 buttons, one of type `dropdown` and one of type `button`.

The button/dropdown can be visualized using either an [svg icon](https://icons.getbootstrap.com/#icons) or text.

```yaml
buttons:
  - type : dropdown
    label: Language
  - type : button
    icon : <svg> ... 
            </svg> 
```
2. Lastly you need to specify the items of your button. So assuming you want to have different language versions, each item will be one of the languages.

```yaml
buttons:
  - type : dropdown
    label: Language

  - type : button
    icon : <svg> ... 
            </svg> 
    items:
      - label: English
        url: url of branch
      - label: Nederlands
        url: url of branch
```
As you can see in the `items:` line, each dropdown option links to the branch of the repository in the respective language.

Note: the `_launch_buttons.yml` file is optional. If it is not present when building HTML, the extension will not install any launch-button assets and no buttons will be shown. Add `_launch_buttons.yml` to enable buttons."

### Setting up your repository for multilingual book

For the implementation to your book, it is handy to create a branch for each language version you want to offer. Make a new branch using for example main as a source. Assuming we want to create a dutch version of you can call this branch `Dutch` or `Nederlands`. 

You will then need to translate the content in the dutch branch to dutch which can take some time. From experience, [DeepL](https://www.deepl.com/en/translator) is a good tool for this but any AI chatbot might be helpful as well. Make sure to proofread the translation.

You'll need to add (merge) the updated `_config.yml` and the new `_launch_buttons.yml` to all of your branches.

### Example

```yaml
buttons:
  - type: dropdown
    icon: <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-globe" viewBox="0 0 16 16">
            <path d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8m7.5-6.923c-.67.204-1.335.82-1.887 1.855A8 8 0 0 0 5.145 4H7.5zM4.09 4a9.3 9.3 0 0 1 .64-1.539 7 7 0 0 1 .597-.933A7.03 7.03 0 0 0 2.255 4zm-.582 3.5c.03-.877.138-1.718.312-2.5H1.674a7 7 0 0 0-.656 2.5zM4.847 5a12.5 12.5 0 0 0-.338 2.5H7.5V5zM8.5 5v2.5h2.99a12.5 12.5 0 0 0-.337-2.5zM4.51 8.5a12.5 12.5 0 0 0 .337 2.5H7.5V8.5zm3.99 0V11h2.653c.187-.765.306-1.608.338-2.5zM5.145 12q.208.58.468 1.068c.552 1.035 1.218 1.65 1.887 1.855V12zm.182 2.472a7 7 0 0 1-.597-.933A9.3 9.3 0 0 1 4.09 12H2.255a7 7 0 0 0 3.072 2.472M3.82 11a13.7 13.7 0 0 1-.312-2.5h-2.49c.062.89.291 1.733.656 2.5zm6.853 3.472A7 7 0 0 0 13.745 12H11.91a9.3 9.3 0 0 1-.64 1.539 7 7 0 0 1-.597.933M8.5 12v2.923c.67-.204 1.335-.82 1.887-1.855q.26-.487.468-1.068zm3.68-1h2.146c.365-.767.594-1.61.656-2.5h-2.49a13.7 13.7 0 0 1-.312 2.5m2.802-3.5a7 7 0 0 0-.656-2.5H12.18c.174.782.282 1.623.312 2.5zM11.27 2.461c.247.464.462.98.64 1.539h1.835a7 7 0 0 0-3.072-2.472c.218.284.418.598.597.933M10.855 4a8 8 0 0 0-.468-1.068C9.835 1.897 9.17 1.282 8.5 1.077V4z"/>
          </svg>
    items:
      - label: English
        url: https://teachbooks.github.io/files-and-folders/EN
      - label: Nederlands
        url: https://teachbooks.github.io/files-and-folders/NL
```

The code in the above cell is the `_launch_buttons.yml` file of a repository called "files-and-folders". The buttons created look like this:

![Custom button](language_button.PNG)

An example of this usage in a book can be found in [this book called Files and Folders](https://teachbooks.io/files-and-folders/EN/intro.html}

## Contribute
This tool's repository is stored on [GitHub](https://github.com/TeachBooks/Sphinx-launch-buttons). The `README.md` of the branch `manual` is also part of the [TeachBooks manual](https://teachbooks.io/manual/intro.html) as a submodule. If you'd like to contribute, you can create a fork and open a pull request on the [GitHub repository](https://github.com/TeachBooks/Sphinx-launch-buttons). To update the `README.md` shown in the TeachBooks manual, create a fork and open a merge request for the [GitHub repository of the manual](https://github.com/TeachBooks/manual). If you intent to clone the manual including its submodules, clone using: `git clone --recurse-submodulesgit@github.com:TeachBooks/manual.git`.
