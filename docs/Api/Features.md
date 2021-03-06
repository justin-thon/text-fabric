## Features

???+ info "Features"
    TF can give you information of all features it has encountered.

??? abstract "TF.featureSets"
    ```python
    TF.featureSets
    ```

    ???+ info "Description"
        Returns a dictionary with keys `nodes`, `edges`, `configs`, `computeds`.

        Under each key there is the set of feature names in that category.
        
        So you can easily test whether a node feature or edge feature is present in the
        dataset you are working with.

        ??? note "configs"
            These are config features, with metadata only, no data. E.g. `otext`.

        ??? note "computeds"
            These are blocks of precomputed data, available under the `C.` API, see below.

    ??? caution "May be unloaded"
        The sets do not indicate whether a feature is loaded or not.
        There are other functions that give you the loaded node features (`Fall()`)
        and the loaded edge features (`Eall()`).

### Node features

???+ info "F"
    The node features API is exposed as `F` (`Fs`) or `Feature` (`FeatureString`).

??? abstract "Fall() aka AllFeatures()"
    ```python
    Fall()
    AllFeatures()
    ```

    ???+ info "Description"
        Returns a sorted list of all usable, loaded node feature names.

??? abstract "F.*feature* aka Feature.*feature*"
    ```python
    F.part_of_speech
    Feature.part_of_speech
    ```

    ???+ info "Description"
        Returns a sub-api for retrieving data that is stored in node features.
        In this example, we assume there is a feature called
        `part_of_speech`.

    ??? caution "Tricky feature names"
        If the feature name is not
        a valid python identifier, you can not use this function,
        you should use `Fs` instead.

??? abstract "Fs(feature) aka FeatureString(feature)"
    ```python
    Fs(feature)
    FeatureString(feature)
    Fs('part-of-speech')
    FeatureString('part-of-speech')
    ```

    ???+ info "Description"
        Returns a sub-api for retrieving data that is stored in node features.
        
    ??? info "feature"
        In this example, in line 1 and 2, the feature name is contained in
        the variable `feature`.

        In lines 3 and 4, 
        we assume there is a feature called
        `part-of-speech`.
        Note that this is not a valid name in Python, yet we
        can work with features with such names.

    ??? explanation "Both methods have identical results"
        Suppose we have just issued `feature = 'pos'.
        Then the result of `Fs(feature)` and `F.pos` is identical.

        In most cases `F` works just fine, but `Fs` is needed in two cases:

        *   if we need to work with a feature whose name is not a valid
            Python name;
        *   if we determine the feature we work with dynamically, at run time.

    ??? note "Simple forms"
        In the sequel we'll give examples based on the simple form only.


??? abstract "F.*feature*.v(node)"
    ```python
    F.part_of_speech.v(node)
    ```

    ???+ info "Description"
        Get the value of a *feature*, such as `part_of_speech` for a node.

    ??? info "node"
        The node whose value for the feature is being retrieved.

??? abstract "F.*feature*.s(value)"
    ```python
    F.part_of_speech.s(value)
    F.part_of_speech.s('noun')
    ```

    ???+ info "Description"
        Returns a generator of all nodes in the canonical order with a given value for a given feature.
        This is an other way to walk through nodes than using `N()`.

    ??? info "value"
        The test value: all nodes with this value are yielded, the others pass through.

    ??? example "nouns"
        The second line gives you all nodes which are nouns according to the corpus.

??? abstract "F.*feature*.freqList()"
    ```python
    F.part_of_speech.freqList(nodeTypes=None)
    ```

    ???+ info "Description"
        Inspect the values of *feature* (in this example: `part_of_speech`)
        and see how often they occur. The result is a
        list of pairs `(value, frequency)`, ordered by `frequency`, highest frequencies
        first.

    ??? info "nodeTypes"
        If you pass a set of nodeTypes, only the values for nodes within those
        types will be counted.


??? abstract "F.otype"
    `otype` is a special node feature and has additional capabilities.

    ???+ info "Description"
        *   `F.otype.slotType` is the node type that can fill the slots (usually: `word`)
        *   `F.otype.maxSlot` is the largest slot number
        *   `F.otype.maxNode` is the largest node number
        *   `F.otype.all` is a list of all *otypes* from big to small (from books through
            clauses to words)
        *   `F.otype.sInterval(otype)` is like `F.otype.s(otype)`, but instead of
            returning you a range to iterate over, it will give you the starting and
            ending nodes of `otype`. This makes use of the fact that the data is so
            organized that all node types have single ranges of nodes as members.

### Edge features

???+ info "E"
    The edge features API is exposed as `E` (`Es`) or `Edge` (`EdgeString`).

??? abstract "Eall() aka AllEdges()"
    ```python
    Eall()
    AllEdges()
    ```

    ???+ info "Description"
        Returns a sorted list of all usable, loaded edge feature names.

??? abstract "E.*feature* aka Edge.*feature*"
    ```python
    E.head
    Feature.head
    ```

    ???+ info "Description"
        Returns a sub-api for retrieving data that is stored in edge features.
        In this example, we assume there is a feature called
        `head`.

    ??? caution "Tricky feature names"
        If the feature name is not
        a valid python identifier, you can not use this function,
        you should use `Es` instead.

??? abstract "Es(feature) aka EdgeString(feature)"
    ```python
    Es(feature)
    EdgeString(feature)
    Es('head')
    EdgeString('head')
    ```

    ???+ info "Description"
        Returns a sub-api for retrieving data that is stored in edge features.
        
    ??? info "feature"
        In this example, in line 1 and 2, the feature name is contained in
        the variable `feature`.

        In lines 3 and 4, 
        we assume there is a feature called
        `head`.

    ??? explanation "Both methods have identical results"
        Suppose we have just issued `feature = 'head'.
        Then the result of `Es(feature)` and `E.pos` is identical.

        In most cases `E` works just fine, but `Es` is needed in two cases:

        *   if we need to work with a feature whose name is not a valid
            Python name;
        *   if we determine the feature we work with dynamically, at run time.

    ??? note "Simple forms"
        In the sequel we'll give examples based on the simple form only.

??? abstract "E.*feature*.f(node)"
    ```python
    E.head.f(node)
    ```

    ???+ info "Description"
        Get the nodes reached by *feature*-edges **from** a certain node.
        These edges must be specified in *feature*, in this case `head`.
        The result is an ordered tuple
        (again, in the *canonical order*. The members of the
        result are just nodes, if `head` describes edges without values. Otherwise
        the members are pairs (tuples) of a node and a value.

        If there are no edges from the node, the empty tuple is returned, rather than `None`.

    ??? info "node"
        The node **from** which the edges in question start.

??? abstract "E.*feature*.t(node)"
    ```python
    E.head.t(node)
    ```

    ???+ info "Description"
        Get the nodes reached by *feature*-edges **to** a certain node.
        These edges must be specified in *feature*, in this case `head`.
        The result is an ordered tuple
        (again, in the *canonical order*. The members of the
        result are just nodes, if `feature` describes edges without values. Otherwise
        the members are pairs (tuples) of a node and a value.

        If there are no edges to `n`, the empty tuple is returned, rather than `None`.

    ??? info "node"
        The node **to** which the edges in question go.

??? abstract "E.*feature*.freqList()"
    ```python
    E.op.freqList(nodeTypesFrom=None, nodeTypesTo=None)
    ```

    ???+ info "Description"
        If the edge feature has no values, simply return the number of node pairs
        between an edge of this kind exists.

        If the edge feature does have values, we 
        inspect them
        and see how often they occur. The result is a
        list of pairs `(value, frequency)`, ordered by `frequency`, highest frequencies
        first.

    ??? info "nodeTypesFrom"
        If not `None`,
        only the values for edges that start from a node with type
        within `nodeTypesFrom`
        will be counted.

    ??? info "nodeTypesTo"
        If not `None`,
        only the values for edges that go to a node with type
        within `nodeTypesTo`
        will be counted.

??? abstract "E.oslots"
    `oslots` is a special edge feature and is mainly used to construct other parts
    of the API. It has less capabilities, and you will rarely need it. It does not
    have `.f` and `.t` methods, but an `.s` method instead.

    ???+ info "Description"
        `E.oslots.s(node)`
        Gives the sorted list of slot numbers linked to a node,
        or put otherwise: the slots that **support** that node.

    ??? info "node"
        The node whose slots are being delivered.

