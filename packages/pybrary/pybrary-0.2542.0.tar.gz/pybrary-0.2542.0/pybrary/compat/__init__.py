from sys import version_info


assert version_info.major == 3
assert version_info.minor >= 9


version = version_info.major, version_info.minor
