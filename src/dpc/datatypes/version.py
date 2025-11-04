from __future__ import annotations
import typing as t

class VersionError(Exception):
    pass


class Version:
    """Represents a version of the game, holding information for that version."""
    
    _VERSION_REFERENCE: dict[str, int] = {
        "1.13.0" : 4,
        "1.14.1" : 4,
        "1.15.1" : 5,
        "1.16.1" : 5,
        "1.16.2" : 6,
        "1.16.3" : 6,
        "1.16.4" : 6,
        "1.16.5" : 6,
        "1.17.0" : 7,
        "1.17.1" : 7,
        "1.18.0" : 8,
        "1.18.1" : 8,
        "1.18.2" : 9,
        "1.19.0" : 10,
        "1.19.1" : 10,
        "1.19.2" : 10,
        "1.19.4" : 12,
        "1.20.0" : 15,
        "1.20.1" : 15,
        "1.20.2" : 18,
        "1.20.3" : 26,
        "1.20.4" : 26,
        "1.20.5" : 41,
        "1.20.6" : 41,
        "1.21.0" : 48,
        "1.21.1" : 48,
        "1.21.4" : 61,
        "1.21.5" : 71,
        "1.21.6" : 80,
        "1.21.7" : 81,
        "1.21.8" : 81
    }
    
    data: tuple[int, int, int]
    
    @t.overload
    def __init__(self, version: str) -> None:
        """Represents a version of the game. Data given from
        a dot seperated string representing the major, minor
        and patch number of the version

        Args:
            version (str): The dot seperated string to parse, organized `[M].[m].[p]`
                            where `M` is the Major update number, `m` is the minor
                            update number and `p` is the patch number
        """
        ...
    
    @t.overload
    def __init__(self, major: int, minor: int, patch: int) -> None: 
        """Represents a version of the game. Data given from
        each seperate argument.

        Args:
            major (int): The major update for this version
            minor (int): The minor update for this version
            patch (int): The patch number
        """
        ...
    
    def __init__(self, *args):
        major: int
        minor: int
        patch: int
        if len(args) == 1:
            # TODO: Better string parsing
            int_args = [int(val) for val in args[0].split(".")][:3]
            major = int_args.pop(0)
            minor = int_args.pop(0)
            patch = int_args.pop(0) if len(int_args) > 0 else 0
        elif len(args) == 3:
            major, minor, patch = [int(arg) for arg in args]
        else:
            raise ValueError("Invalid number of arguments for Version init")
        self.data = (major, minor, patch)
    
    def __str__(self):
        return ".".join([str(val) for val in self.data])
    
    def __hash__(self):
        return object.__hash__(self)

    def __eq__(self, value: Version) -> bool:
        if not isinstance(value, Version):
            return False
        return (self.major == value.major) and (self.minor == value.minor) and (self.patch == value.patch)
    
    # TODO: Optimize this function
    def __gt__(self, other: Version) -> bool:
        if not isinstance(other, Version):
            return False
        if self.major > other.major:
            return True
        if self.minor > other.minor:
            return True
        if self.patch > other.patch:
            return True
        return False
    
    def __lt__(self, other: Version) -> bool:
        if not isinstance(other, Version):
            return False
        if self.major < other.major:
            return True
        if self.minor < other.minor:
            return True
        if self.patch < other.patch:
            return True
        return False
    
    def __ge__(self, other: Version) -> bool:
        if not isinstance(other, Version):
            return False
        return not self.__lt__(other)
    
    def __le__(self, other: Version) -> bool:
        if not isinstance(other, Version):
            return False
        return not self.__gt__(other)
    
    @classmethod
    def minimum(cls) -> Version:
        """Returns the minimum allowed version

        Returns:
            Version: A version instance of the lowest allowed update
        """
        instance = object.__new__(cls)
        instance.data = (1, 13, 0)
        return instance
    
    @classmethod
    def maximum(cls) -> Version:
        """Creates an instance of version set to the highest
        allowed version of the game

        Returns:
            Version: A version instance of the highest allowed update
        """
        instance = object.__new__(cls)
        instance.data = (1, 21, 8)
        return instance
    
    @classmethod
    def get_pack_reference(cls, version: Version | str) -> int:
        """Returns the integer representing the required pack
        number for a given version, or 0 if the given version
        is not found within the current pack reference.

        Args:
            version (Version | str): The version to obtain the reference for
                                        as a version instance or a dot seperated
                                        string

        Returns:
            int: The pack reference number
        """
        return cls._VERSION_REFERENCE.get(str(version), -1)
    
    @property
    def major(self) -> int:
        return self.data[0]
    
    @major.setter
    def major(self, value: int) -> None:
        self.data[0] = value
    
    @property
    def minor(self) -> int:
        return self.data[1]
    
    @minor.setter
    def minor(self, value: int) -> None:
        self.data[1] = value
    
    @property
    def patch(self) -> int:
        return self.data[2]
    
    @patch.setter
    def patch(self, value: int) -> None:
        self.data[2] = value
    
    @property
    def pack_reference(self) -> int:
        return Version.get_pack_reference(self)


class VersionRange:
    """Represents a range of versions between an upper bound and a lower bound"""
    
    _range: tuple[Version | None, Version | None]
    
    def __init__(self, lower: Version | str | None = None, upper: Version | str | None = None):
        """Creates a new instance representing a range of versions between
        an upper and lower bound. If the passed types of the bounds are
        strings then they will attempt to be interpreted as versions. Each argument
        is optional and if None is passed (or the argument default is left), then
        the range will represent all versions up to (in the case of a given max) or
        after (in the case of a given min) the passed argument, and accessing the
        default value will return `Version.min()` or `Version.max()`.

        Args:
            lower (Version | str | None, optional): The lower bound, if the argument is not 
                                                    passed it will default to the lowest 
                                                    available version. Defaults to None.
            upper (Version | str | None, optional): The upper bound, if the argument is not 
                                                    passed it will default to the highest 
                                                    available version. Defaults to None.
        """
        self._range = (
            Version(lower) if isinstance(lower, str) else lower, 
            Version(upper) if isinstance(upper, str) else upper
        )
    
    def __str__(self) -> str:
        return f"VersionRange({self.lower}, {self.upper})"
    
    @classmethod
    def from_range(cls, v1: VersionRange, v2: VersionRange) -> VersionRange:
        """Creates a new version range from the ranges given,
        taking the highest upper bound and the lowest lower
        bound to create a new range that encapsulates both
        of the input ranges.

        Args:
            v1 (VersionRange): The first range to check
            v2 (VersionRange): The second range to check

        Returns:
            VersionRange: The version range that encapsulates
                            both given ranges
        """
        instance: VersionRange = VersionRange.__new__(VersionRange)
        instance._range = (
            min(v1.lower, v2.lower),
            max(v1.upper, v2.upper)
        )
        return instance
    
    @classmethod
    def from_overlap(cls, v1: VersionRange, v2: VersionRange) -> VersionRange | None:
        """Creates a new version range from the overlap in the
        ranges given. If no overlap is given this function returns
        None

        Args:
            v1 (VersionRange): The first range to check
            v2 (VersionRange): The second range to check

        Returns:
            VersionRange | None: The version range representing
                                    the overlap across the given
                                    ranges
        """
        instance: VersionRange = VersionRange.__new__(VersionRange)
        instance._range = {
            max(v1.lower, v2.lower),
            min(v1.upper, v2.upper)
        }
        return instance if instance.upper < instance.lower else None
    
    @classmethod
    def largest(cls) -> VersionRange:
        instance: VersionRange = super().__new__(cls)
        instance._range = {
            Version.minimum(),
            Version.maximum()
        }

    def contains(self, version: Version) -> bool:
        """Checks if a version passed is within the
        bounds set by this version range.

        Args:
            version (Version): The version to validate

        Returns:
            bool: If the given version is within contained
                    by this version range
        """
        return (version >= self.lower) and (version <= self.upper)
    
    @property
    def has_lower_bound(self) -> bool:
        return self._range[0] is not None
    
    @property
    def lower(self) -> Version:
        return self._range[0] or Version.min()
    
    @lower.setter
    def lower(self, value: Version | str | None) -> None:
        self._range = (Version(value) if isinstance(value, str) else value, self.upper)
    
    @property
    def has_upper_bound(self) -> bool:
        return self._range[1] is not None
    
    @property
    def upper(self) -> Version:
        return self._range[1] or Version.max()
    
    @upper.setter
    def upper(self, value: Version | str | None) -> None:
        self._range = (self.lower, Version(value) if isinstance(value, str) else value)

class Versionable(object):
    """An interface that makes an object able to be versioned properly"""
    
    _ALLOWED_RANGE: VersionRange
    
    @classmethod
    def allowed_for_version(cls, version: Version) -> bool:
        return cls._ALLOWED_RANGE.contains(version)

# TODO: Versioning class and function decorator that adds a VersionRange to an object.