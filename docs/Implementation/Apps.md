# Apps

??? abstract "About"
    Text-Fabric is a generic engine to process text and annotations.

    When working with specific corpora, we want to have more power at our fingertips.

    We need extra power on top of the core TF engine.

    The way we have chosen to do it is via *apps*.
    An app is a bunch of extra functions that *know* the structure of a specific corpus.

    In particular, an app knows how to produce plain representations
    and pretty displays of nodes of each type in the corpus.

    For a list of current apps, see [Corpora](../About/Corpora.md)

## Components

??? abstract "App components"
    The apps themselves are modules inside 
    [apps]({{tfght}}/{{b_apps}})

    For each *app*, you find there a subfolder *app* with:

    ??? abstract "static"
        A folder with styles, fonts and logos, to be used by web servers such as the the
        [text-fabric browser](../Server/Web.md).

        In particular, `display.css` contains the styles used for pretty displays.
        These styles will be programmatically combined with other styles,
        to deliver them to the TF browser on the one hand, and to Jupyter notebooks
        on the other hand.

    ??? abstract "config.py"
        Settings to set up a browsing experience and to feed the specific AP
        for this app.

        The TF kernel, web server and browser need settings:

        setting | example | description
        --- | --- | ---
        PROTOCOL | `http://` | protocol of website
        HOST | `localhost` | server address of the website
        PORT['kernel'] | `18981` | port through wich the TF kernel and the web server communicate
        PORT['web'] | `8101` | port at which the TF web server listens for requests
        OPTIONS | tuple | names of extra options for searching and displaying query results

        The app itself is driven by the following settings

        setting | type | description
        --- | --- | ---
        ORG | string | GitHub organization name of the main data source of the corpus
        REPO | string | GitHub repository name of the main data source of the corpus
        RELATIVE | string | Path to the *tf* directory within the GitHub repository of the main data
        CORPUS | string | Descriptive name of the main corpus
        VERSION | string | Version of the main corpus that is used in the TF browser
        DOI_TEXT | string | Text of the Digital Object Identifier pointing to the main corpus
        DOI_URL | url | Digital Object Identifier that points to the main corpus
        DOC_URL | url | Base url for the online documentation of the main corpus
        DOC_INTRO | string | Relative url to the introduction page of the documentation of the main corpus 
        CHAR_TEXT | string | Text of the link pointing to the character table of the relevant Unicode blocks
        CHAR_URL | string | Link to the character table of the relevant Unicode blocks
        FEATURE_URL | url | Url to feature documentation. Contains `{feature}` and `{version}` which can be filled in later with the actual feature name and version tag
        MODULE_SPECS | tuple of dicts | Provides information for standard data modules that will be loaded together with the main corpus: *org*, *repo*, *relative*, *corpus*, *docUrl*, *doi* (text and link)
        ZIP | list | data directories to be zipped for a release, given as either `(org, repo, relative)` or `repo` (with org and relative taken from main corpus); only used by `text-fabric-zip` when collecting data into zip files to be attached to a GitHub release
        CONDENSE_TYPE | string | the default node type to condense search results in, e.g. `verse` or `tablet`
        NONE_VALUES | set | feature values that are deemed uninformative, e.g. `None`, `'NA'`
        STANDARD_FEATURES | set | features that are shown by default in all pretty displays
        EXCLUDED_FEATURES | set | features that are present in the data source but will not be loaded for the TF browser
        NO_DESCEND_TYPES | set | when representing nodes as text in exports from the TF browser, node of type in this set will not be expanded to their slot occurrences; e.g. `lex`: we do not want represent lexeme nodes by their list of occurrences
        EXAMPLE_SECTION | html | what a passage reference looks like in this corpus; may have additional information in the form of a link; used in the Help of the TF browser
        EXAMPLE_SECTION_TEXT | string | what a passage reference looks like in this corpus; just the plain text; used in the Help of the TF browser
        SECTION_SEP1 | string | separator between main and secondary sections in a passage reference; e.g. the space in `Genesis 1:1`
        SECTION_SEP2 |string |  separator between secondary and tertiary sections in a passage reference; e.g. the `:` in `Genesis 1:1`
        FORMAT_CSS | dict | mapping between TF text formats and CSS classes; not all text formats need to be mapped
        DEFAULT_CLS | string | default CSS class for text in a specific TF text format, when no format-specific class is given in FORMAT_CSS
        DEFAULT_CLS_ORIG | string | default CSS class for text in a specific TF text format, when no format-specific class is given in FORMAT_CSS; and when the TF text format contains the `-orig-` string; used to specify classes for text in non-latin scripts
        CLASS_NAMES | dict | mapping between node types and CSS classes; used in pretty displays to format the representations of nodes of that type 
        FONT_NAME | string | font family name to be used in CSS for representing text in original script
        FONT | string | file name of the offline font specified in FONT_NAME
        FONTW | string | file name of the webfont specified in FONT_NAME
        BROWSE_NAV_LEVEL | int | the section level up to which the browser shows a hierarchical tree. Either 1 or 2
        BROWSE_CONTENT_PRETTY | bool | whether the content is shown as a list of subsectional items contained in the selected item or as a pretty display of the item itself

    ??? abstract "app.py"
        The functionality specific to the corpus in question, organized as an extended
        TF api. In the code you see this stored in variables with name `app`.

        In order to be an app that TF can use, `app` should provide the following attributes:

        attribute | kind | description
        --- | --- | ---
        webLink | method | given a node, produces a link to an online description of the corresponding object (to [shebanq]({{shebanq}}) or [cdli]({{cdli}})) 
        \_plain | method | given a node, produce a plain representation of the corresponding object: not the full structure, but something that identifies it
        \_pretty | method | given a node, produce elements of a pretty display of the corresponding object: the full structure

## Implementation

??? abstract "App support"
    Apps turn out to have several things in common that we want to deal with generically.
    These functions are collected in the
    [api]({{tfghb}}/{{c_apps}})
    modules of TF.

??? abstract "Two contexts"
    Most functions with the `app` argument are meant to perform their duty
    in two contexts:

    * when called in a Jupyter notebook they deliver output meant
      for a notebook output cell,
      using methods provided by the `ipython` package.
    * when called by the web app they deliver output meant for the TF browser website,
      generating raw HTML.

    The `app` is the rich app specific API, and when we construct this API,
    we pass the information
    whether it is constructed for the purposes of the Jupyter notebook,
    or for the purposes of the web app.

    We pass this information by setting the attribute `_asApp` on the `app`. 
    If it is set, we use the `app` in the web app context.

    Most of the code in such functions is independent of `_asApp`.
    The main difference is how to output the result:
    by a call to an IPython display method, or by
    returning raw HTML.

    ??? note "\_asApp"
        The `app` contains several display functions. By default
        they suppose that there is a Jupyter notebook context in which
        results can be rendered with `IPython.display` methods.
        But if we operate in the context of a web-interface, we need to generate
        straight HTML. We flag the web-interface case as `_asApp == True`.
