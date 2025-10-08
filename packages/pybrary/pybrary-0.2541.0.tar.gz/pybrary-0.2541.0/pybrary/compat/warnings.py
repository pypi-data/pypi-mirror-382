from pybrary.compat import version


if version < (3, 13):
    from pybrary.compat.backport.warnings import deprecated
else:
    from warnings import deprecated
