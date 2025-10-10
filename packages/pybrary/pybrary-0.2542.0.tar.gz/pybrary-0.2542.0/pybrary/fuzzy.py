from re import escape, compile


def fuzzy_select(pattern, inputs, protector=None, decorate=None):
    '''Fuzzy selector.

    Returns a weigthed and sorted selection of items
    from (decorated) inputs based on "fuzzy" pattern.

    pattern   :
        A string representing the pattern to be found "fuzzily".

    inputs    :
        An iterable of strings to be filtered.

    protector :
        The string used as a delimitor of "protected" sections in pattern.
        defaults to ".

    decorate  :
        An optional callable to apply on each input before filtering.

    returns   :
        A generator of selectioned inputs.
    '''

    # define local variables.
    parts, pro, deco = [], protector or '"', decorate

    # make pattern spliter.
    split = compile('({pro}.*?{pro})'.format(pro=pro)).split

    # define local functions
    app, ext, pat = parts.append, parts.extend, split(pattern)

    # extract sub-patterns from pattern.
    [app(p.strip(pro)) if pro in p else ext(tuple(p.strip())) for p in pat]

    # build pattern finder.
    search = compile('.*?'.join(map(escape, parts))).search

    # decorate inputs if needed.
    decorated = map(deco, inputs) if callable(deco) else inputs

    # select matching inputs.
    matching = ((i, m) for i, m in enumerate(map(search, decorated)) if m)

    # apply weigths to matchings
    weighted = ((len(m.group()), m.start(), i) for i, m in matching)

    # sort selection.
    suggested = [inputs[w[-1]] for w in sorted(weighted)]

    return suggested
