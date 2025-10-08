import logging
from collections import defaultdict, deque
from typing import Any, Generator, Optional, Self, Union
from urllib.parse import unquote

from detdevlib.utils.etc import safe_int

_NO_DEFAULT = object()  # sentinel indicating no default was set.
_NO_VALUE = object()  # sentinel indicating no value was found.

logger = logging.getLogger(__name__)


class JSONPointer:
    """Represents an RFC 6901 compliant JSON Pointer.

    A JSON Pointer is a string syntax for identifying a specific value within a
    JSON document. It is a Unicode string containing a sequence of zero or more
    reference tokens, each prefixed by a '/' character.

    Attributes:
        _tokens (tuple[str, ...]): A tuple of unescaped string tokens that
            constitute the pointer.
    """

    __slots__ = ("_tokens",)  # Declare attributes, saves memory.

    @staticmethod
    def _escape_token(part: str) -> str:
        """Escapes a string token for use in a JSON Pointer.

        Replaces '~' with '~0' and '/' with '~1' as per RFC 6901.

        Args:
            part (str): The token to escape.

        Returns:
            str: The escaped token.
        """
        return part.replace("~", "~0").replace("/", "~1")

    @staticmethod
    def _unescape_token(part: str) -> str:
        """Unescapes a string token from a JSON Pointer.

        Replaces '~1' with '/' and '~0' with '~' as per RFC 6901.

        Args:
            part (str): The token to unescape.

        Returns:
            str: The unescaped token.
        """
        return part.replace("~1", "/").replace("~0", "~")

    @classmethod
    def _resolve_array_index(cls, array: list, token: str):
        """Resolves a string token to a valid array index.

        Supports integer strings and the special '-' token, which refers to the
        end of the array (i.e., the index for appending a new element).

        Args:
            array (list): The list context for which the index is resolved.
            token (str): The string token representing the index.

        Returns:
            int: The resolved integer index.

        Raises:
            ValueError: If the token is not a valid non-negative integer or '-'.
        """
        if token == "-":
            return len(array)
        index = safe_int(token)
        if index is None or index < 0:
            raise ValueError(f"Invalid index '{token}' for array '{array}'")
        return index

    @classmethod
    def _index_object(cls, obj: Any, token: str, default=_NO_DEFAULT) -> Any:
        """Retrieves a value from a JSON-like object using a single token.

        Accesses a value from a dictionary by key or a list by index.

        Args:
            obj (Any): The dictionary or list to access.
            token (str): The key or index string to use for access.
            default (Any): A default value to return if the token is not found.
                If not provided, a ValueError is raised.

        Returns:
            Any: The value found at the specified token, or the default value.

        Raises:
            ValueError: If the token is not found and no default is provided.
        """
        if isinstance(obj, dict):
            if token in obj:
                return obj[token]
        elif isinstance(obj, list):
            try:
                index = cls._resolve_array_index(obj, token)
                if 0 <= index < len(obj):
                    return obj[index]
            except ValueError:
                pass
        if default is _NO_DEFAULT:
            raise ValueError(f"Token '{token}' not found in {obj}'")
        return default

    @classmethod
    def _enter_object(cls, obj: Any, token: str) -> Any:
        """Traverses into a JSON-like object, creating containers if they don't exist.

        For dictionaries, it returns the value for the given token, creating a new
        empty dictionary if the key is missing. For lists, it can access an existing
        index or append a new dictionary if the index points to the end of the list.

        Args:
            obj (Any): The dictionary or list to traverse.
            token (str): The key or index string to use for traversal.

        Returns:
            Any: The existing or newly created nested object.

        Raises:
            ValueError: If the token is an invalid index for the list or if the
                object is not a list or dictionary.
        """
        if isinstance(obj, dict):
            return obj.setdefault(token, {})
        elif isinstance(obj, list):
            index = cls._resolve_array_index(obj, token)
            if index == len(obj):
                obj.append({})
                return obj[index]
            elif 0 <= index < len(obj):
                return obj[index]
        raise ValueError(f"Invalid token '{token}' for obj '{obj}'")

    @classmethod
    def _parse(cls, pointer_str: str) -> tuple[str, ...]:
        """Parses a JSON Pointer string into a tuple of unescaped tokens.

        Args:
            pointer_str (str): The JSON Pointer string (e.g., "/a/b/0").

        Returns:
            tuple[str, ...]: A tuple of unescaped tokens.

        Raises:
            ValueError: If the pointer string is not empty and does not start
                with '/'.
        """
        if pointer_str == "":
            return tuple()
        if not pointer_str.startswith("/"):
            raise ValueError(
                f"JSON Pointer must start with '/' or be empty: '{pointer_str}'"
            )
        tokens = pointer_str[1:].split("/")
        return tuple(cls._unescape_token(token) for token in tokens)

    def __init__(
        self, p: Union[str, list[str | int], tuple[str | int, ...], Self, None] = None
    ):
        """Initializes a JSONPointer instance.

        Args:
            p (Union[str, list[str | int], tuple[str | int, ...], Self, None], optional):
                The source to create the pointer from. Can be a pointer string,
                a list/tuple of tokens, another JSONPointer instance, or None for
                a root pointer. Defaults to None.

        Raises:
            TypeError: If `p` is of an unsupported type.
        """
        if p is None:
            self._tokens: tuple[str, ...] = tuple()
        elif isinstance(p, str):
            self._tokens = self._parse(p)
        elif isinstance(p, (list, tuple)):
            self._tokens = tuple(str(token) for token in p)
        elif isinstance(p, JSONPointer):
            self._tokens = p._tokens
        else:
            raise TypeError(f"Invalid pointer type: {type(p)}")

    def __str__(self):
        return "".join(f"/{self._escape_token(t)}" for t in self._tokens)

    def __repr__(self):
        return f"{self.__class__.__name__}({str(self)!r})"

    def __truediv__(self, tokens: Union[str, int, Self]) -> Self:
        if isinstance(tokens, self.__class__):
            return self.__class__(self._tokens + tokens._tokens)
        if isinstance(tokens, str):
            return self.__class__(self._tokens + (tokens,))
        if isinstance(tokens, int):
            return self.__truediv__(str(tokens))
        raise TypeError(f"{tokens} is of invalid type {type(tokens)}")

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._tokens == other._tokens

    def __hash__(self):
        return hash(self._tokens)

    def __len__(self):
        return len(self._tokens)

    def __iter__(self):
        return iter(self._tokens)

    @property
    def last_token(self):
        """Returns the last token in this pointer."""
        if self.is_root:
            return None
        return self._tokens[-1]

    def set_last_token(self, last_token: str) -> Self:
        """Creates a new pointer by replacing the last token of the current one.

        Args:
            last_token (str): The new final token.

        Returns:
            Self: A new JSONPointer instance with the replaced final token.

        Raises:
            ValueError: If called on a root pointer (which has no tokens).
        """
        if self.is_root:
            raise ValueError("Cannot set final of a root pointer.")
        return JSONPointer(self._tokens[:-1] + (last_token,))

    @property
    def tokens(self) -> tuple[str, ...]:
        """Returns the tokens of this pointer."""
        return self._tokens

    @property
    def is_root(self) -> bool:
        """True if the pointer is a root pointer, False otherwise."""
        return len(self._tokens) == 0

    def exists(self, obj) -> bool:
        """Checks if the pointer can resolve to a value within a given object.

        Args:
            obj (Any): The JSON-like object to check.

        Returns:
            bool: True if the pointer resolves to a value, False otherwise.
        """
        try:
            self.get(obj)
            return True
        except ValueError:
            return False

    def parent(self) -> Self:
        """Returns the parent pointer.

        The parent is a new pointer with the last token removed. If the pointer
        is already the root, it returns itself.

        Returns:
            Self: A new JSONPointer instance representing the parent, or self if
                  it is the root pointer.
        """
        if self.is_root:
            return self
        return self.__class__(self._tokens[:-1])

    def get(self, obj, default=_NO_DEFAULT) -> Any:
        """Resolves the pointer against a JSON-like object to get a value.

        Args:
            obj (Any): The object to resolve the pointer against.
            default (Any, optional): A value to return if the pointer cannot be
                resolved. If not provided, a ValueError is raised.

        Returns:
            Any: The value at the pointer's location, or the default value if
                 provided and the path does not exist.

        Raises:
            ValueError: If the pointer cannot be resolved and no default is given.
        """
        for token in self._tokens:
            obj = self._index_object(obj, token, default)
            if obj is default:
                return default
        return obj

    def put(self, obj, value):
        """Sets a value in a JSON-like object at the location specified by the pointer.

        This method will create nested dictionaries as needed to fulfill the path.
        It can also set or append values in lists.

        Args:
            obj (Any): The object to modify.
            value (Any): The value to set at the pointer's location.

        Returns:
            Self: The current pointer instance.

        Raises:
            ValueError: If attempting to set the root, use an invalid list index,
                or if a path segment cannot be created (e.g., trying to set a key
                on a non-dict object).
        """
        if self.is_root:
            raise ValueError(f"Cannot put value at the root")
        *tokens, last_token = self.tokens
        for token in tokens:
            obj = self._enter_object(obj, token)
        if isinstance(obj, dict):
            obj[last_token] = value
        elif isinstance(obj, list):
            index = self._resolve_array_index(obj, last_token)
            if index == len(obj):
                obj.append(value)
            elif 0 <= index < len(obj):
                obj[index] = value
            else:
                raise ValueError(f"Array index '{index}' out of bounds.")
        else:
            raise ValueError(f"Cannot put on obj {obj} of type {type(obj)}.")
        return self

    def pop(self, obj):
        """Removes and returns a value from an object at the pointer's location.

        Args:
            obj (Any): The object to modify.

        Returns:
            Any: The value that was removed.

        Raises:
            ValueError: If the pointer is the root, the path does not exist,
                the index is out of bounds, or the target object does not support
                popping (i.e., is not a list or dict).
            KeyError: If a key in the path does not exist in a dictionary.
        """
        if not self._tokens:
            raise ValueError(f"Cannot pop the root")
        *tokens, last_token = self.tokens
        for token in tokens:
            obj = self._index_object(obj, token)

        if isinstance(obj, dict):
            if last_token not in obj:
                raise KeyError(f"Key '{last_token}' not in {obj}")
            return obj.pop(last_token)
        if isinstance(obj, list):
            index = self._resolve_array_index(obj, last_token)
            if not 0 <= index < len(obj):
                raise ValueError(f"Array index '{index}' out of bounds.")
            return obj.pop(index)
        raise ValueError(f"Cannot pop from obj {obj} of type {type(obj)}.")

    def resolve(self, obj) -> Optional[Self]:
        """Resolves a JSON reference string found at the pointer's location.

        First, it gets the value at the current pointer's location within `obj`.
        If that value is a JSON reference string (e.g., "#/definitions/User"),
        it parses this string into a new JSONPointer object.

        Args:
            obj (Any): The object to resolve the reference from.

        Returns:
            Optional[Self]: A new JSONPointer instance parsed from the reference
                string, or None if the pointer does not exist in the object or
                the value is not a valid reference string.
        """
        reference_string = self.get(obj, default=_NO_VALUE)
        if reference_string is _NO_VALUE:
            logger.warning(f"cannot resolve {self} for obj {obj}")
            return None  # Pointer points to no existing value
        return parse_reference(reference_string)


def get_reference(pointer: JSONPointer, url: str = "") -> str:
    """Formats a JSONPointer into a JSON reference string.

    A JSON reference is a string that identifies a value in a JSON document,
    combining an optional URI with a JSON Pointer fragment.

    Args:
        pointer (JSONPointer): The pointer to format.
        url (str, optional): An optional URL or URI to prepend to the
            reference. Defaults to "".

    Returns:
        str: The fully formed JSON reference string (e.g., "http://example.com#/a/b").
    """
    return f"{url}#{pointer}"


def parse_reference(ref_str: str) -> Optional[JSONPointer]:
    """Parses a JSONPointer from a JSON reference string.

    Extracts the fragment identifier from a reference string (the part after '#')
    and parses it into a JSONPointer object.

    Args:
        ref_str (str): The JSON reference string (e.g., "#/a/b").

    Returns:
        Optional[JSONPointer]: A JSONPointer object if the fragment can be
            parsed successfully. Returns None if the string is not a valid
            reference (e.g., missing '#', contains a URL part, or has a
            malformed fragment).
    """
    if not isinstance(ref_str, str):
        logger.warning(
            f"reference string {ref_str} has unexpected type {type(ref_str)}"
        )
        return None
    if not "#" in ref_str:
        logger.warning(f"reference string is missing # symbol {ref_str}")
        return None
    url_part, fragment = ref_str.split("#", maxsplit=1)
    if url_part:
        logger.warning(f"reference string has unsupported url {url_part}")
        return None
    try:
        return JSONPointer(unquote(fragment))
    except Exception as e:
        logger.warning(f"cannot parse JSONPointer because of {e}")
        return None


def bfs(obj: Any) -> Generator[tuple[JSONPointer, Any], None, None]:
    """Performs a breadth-first search (BFS) on a JSON-like object.

    Iterates through all keys and values in nested dictionaries and lists,
    yielding the pointer and value for each item encountered.

    Args:
        obj (Any): The JSON-like object (dict, list, etc.) to traverse.

    Yields:
        Generator[tuple[JSONPointer, Any], None, None]: A generator that yields
            tuples of (JSONPointer, value) for each item in the object.
    """
    queue = deque([(JSONPointer(), obj)])

    while queue:

        p, obj = queue.popleft()
        yield p, obj

        if isinstance(obj, dict):
            for key, value in obj.items():
                queue.append((p / key, value))
        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                queue.append((p / str(index), value))


def collect_references(obj: Any) -> dict[JSONPointer, list[JSONPointer]]:
    """Finds and groups all JSON references (`$ref`) within a JSON-like object.

    This function traverses the object and identifies all keys named "$ref".
    It parses the string value of each reference and collects them into a
    dictionary.

    Args:
        obj (Any): The JSON-like object to scan for references.

    Returns:
        dict[JSONPointer, list[JSONPointer]]: A dictionary where keys are the
            parsed `JSONPointer` objects from the `$ref` values (the targets),
            and values are lists of `JSONPointer` objects pointing to the
            locations of those `$ref` keys (the sources).
    """
    res = defaultdict(list)
    for p1, obj in bfs(obj):
        if p1.last_token == "$ref" and isinstance(obj, str):
            p2 = parse_reference(obj)
            if p2 is not None:
                res[p2].append(p1)
    return res
