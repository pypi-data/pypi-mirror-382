"""
Encode user-friendly values into internal formats used by the application,
and decoder the values back into user-friendly values.
"""

#===============================================================================
# Imports
#===============================================================================

from difflib import get_close_matches
from typing import Any, Dict, List, Optional, Set

from mhi.common.warnings import warn, FuzzyMatchWarning


#===============================================================================
# Coder/Decoder
#===============================================================================

class Codec:
    """
    Codec: Coder / Decoder

    Encode from user-friendly values into an internal value format,
    and decode from the internal format into (ideally) a user-friendly
    value.
    """

    def encode(self, value: Any) -> Any:    # pylint: disable=unused-argument
        """
        Encode a user-friendly value into an internal format

        Parameters:
           value: the value to encode

        Returns:
            the encoded value
        """

        raise NotImplementedError()

    def decode(self, value: Any) -> Any:    # pylint: disable=unused-argument
        """
        Decode an internal format value into a more user-friendly format

        Parameters:
           value: the value to decode

        Returns:
            the decoded value
        """

        raise NotImplementedError()


    def range(self):
        """
        Returns the range of values that this codec will encode,
        as in, maybe passed to :meth:`.encode` and will
        be returned by :meth:`.decode`.
        """

        raise NotImplementedError()


#===============================================================================
# Boolean Coder/Decoder
#===============================================================================

class BooleanCodec(Codec):
    """
    Boolean Coder / Decoder

    Convert Python boolean values to/from the strings `"true"` and `"false"`,
    used by MHI application serialization.
    """

    def encode(self, value: Any) -> str:
        """
        Encode a boolean into an MHI serialization string

        Parameters:
           value (bool): the value to encode

        Returns:
            str: the "encoded" string `"true"` or `"false"`
        """

        flag = None
        if isinstance(value, bool):
            flag = value
        elif isinstance(value, str):
            if value.lower() in {"false", "no", "0"}:
                flag = False
            elif value.lower() in {"true", "yes", "1"}:
                flag = True
        elif isinstance(value, int):
            if value == 0:
                flag = False
            elif value == 1:
                flag = True

        if flag is None:
            raise ValueError("Not a boolean value: "+repr(value))

        if not isinstance(value, bool):
            warn("Not a boolean value: " + repr(value))

        return "true" if flag else "false"

    def decode(self, value: str) -> bool:
        """
        Decode a boolean from an MHI serialization string

        Parameters:
           value (str): the string `"true"` or `"false"`

        Returns:
            bool: the decoded value
        """

        return value.lower() == "true"


    def range(self) -> Set[bool]:
        """
        Returns the range of values that this codec will encode,
        as in, maybe passed to :meth:`.encode` and will
        be returned by :meth:`.decode`.

        Returns:
            ``{False, True}``
        """

        return {False, True}


#===============================================================================
# Map Coder/Decoder
#===============================================================================

class MapCodec(Codec):
    """
    Map Coder / Decoder

    Convert Python values to/from the strings,
    used by MHI application serialization.
    """

    def __init__(self, code, *, extras=None):
        self._encode = code
        self._decode = {val: key for key, val in code.items()}
        self._range = frozenset(self._encode.keys())
        if extras:
            for extra_code, values in extras.items():
                for value in values:
                    self._encode[value] = extra_code

    def encode(self, value: Any) -> str:
        """
        Encode a value into an MHI serialization string

        Parameters:
           value: the value to encode

        Returns:
            str: the encoded string
        """

        if value not in self._encode:
            encoded = str(value)
            if encoded in self._decode:
                return encoded
            if encoded in self._encode:
                value = encoded

        return self._encode[value]

    def decode(self, value: str) -> Any:
        """
        Decode a value from an MHI serialization string

        Parameters:
           value (str): the value to decode

        Returns:
            the decoded value
        """

        return self._decode[value]

    def range(self) -> Set[Any]:
        """
        Returns the range of values that this codec will encode,
        as in, maybe passed to :meth:`.encode` and will
        be returned by  :meth:`.decode`.

        Returns:
            frozenset: value which can be encoded by the codec.
        """

        return set(self._range)

    def __repr__(self):
        code = ", ".join(f"{val!r}: {key!r}"
                         for key, val in self._decode.items())
        return f"MapCodec({{{code}}})"


#===============================================================================
# Keyword Coder/Decoder
#===============================================================================

class KeywordCodec(Codec):
    """
    Keyword Codec

    Encode values for specific keys of a dictionary from user-friendly values
    into an internal value format, and decode values for those specific keys
    from the internal format into (ideally) a user-friendly value.
    """

    def encodes(self, keyword: str):        # pylint: disable=unused-argument
        """
        Predicate, indicating whether or not this keyword codec will encode
        and decode a particular keyword

        Parameters:
            keyword (str): keyword to test

        Returns:
            bool: ``True`` if this codec handles the ``keyword``,
            ``False`` otherwise
        """

        raise NotImplementedError()

    def encode_all(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encode all values in the given dictionary which are handled by this
        codec.  Values for unrecognized keywords are unchanged.

        Parameters:
            kwargs (dict): a dictionary of keyword-value pairs

        Returns:
            dict: A new dictionary containing encoded values, where supported.
        """

        return {key: self.encode(value) if self.encodes(key) else value
                for key, value in kwargs.items()}

    def decode_all(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decode all values in the given dictionary which are handled by this
        codec.  Values for unrecognized keywords are unchanged.

        Parameters:
            kwargs (dict): a dictionary of keyword-value pairs

        Returns:
            dict: A new dictionary containing decoded values, where supported.
        """

        return {key: self.decode(value) if self.encodes(key) else value
                for key, value in kwargs.items()}


#===============================================================================
# CodecMap
#===============================================================================

class CodecMap:
    """
    A collection of codecs for encoding/decoding a dictionary of values

    The dictionary keys are used to select the codec used for that entry.
    """

    def __init__(self, **codecs):
        self._codecs = codecs

    def _encode(self, keyword: str, value: Any) -> Any:
        codec = self._codecs.get(keyword)
        if codec is not None:
            value = codec.encode(value)
        return value

    def _decode(self, keyword: str, value: str) -> Any:
        codec = self._codecs.get(keyword)
        if codec is not None:
            value = codec.decode(value)
        return value

    def encode_all(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encode a dictionary of values
        """

        return {key: self._encode(key, value) for key, value in kwargs.items()}

    def decode_all(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decode a dictionary of values
        """

        return {key: self._decode(key, value) for key, value in kwargs.items()}

    def range(self, keyword) -> Any:
        """
        Return the valid range for a given parameter (key)
        """

        return self._codecs[keyword].range()


#===============================================================================
# Coder/Decoder
#===============================================================================

class SimpleCodec(KeywordCodec):
    """
    Keyword Codec

    Encode values for specific keys of a dictionary from user-friendly values
    into an internal value format, and decode values for those specific keys
    from the internal format into (ideally) a user-friendly value.

    Parameters:
        code_dict (dict): A dictionary used to translate user-friendly values
          into internal values.
        **codes: additional keyword-value translation pairs.

    Example:
        A codec which converts fruit names into integers::

			>>> codec = SimpleCodec(apple=1, banana=2, pear=3)
			>>> codec.keywords('fruit')
			>>> codec.encode('apple')
			1
			>>> codec.decode(2)
			'banana'
			>>> codec.encode_all({'animal': 'lion', 'fruit': 'pear'})
			{'animal': 'lion', 'fruit': 3}
    """

    def __init__(self, code_dict=None, **codes):

        if code_dict is None:
            self._code = {**codes}
        else:
            self._code = dict(code_dict, **codes)
        self._decode = {str(val): key for key, val in self._code.items()}
        self._keys = set()

    def alternates(self, code_dict, **codes):
        """
        Provide additional encodings aliases for the codec.
        These additional options must not duplicate any existing user-friendly
        keywords, and must not introduce any new values to the mapping.

        For instance, a codec may defined the mapping 'EMTPY' => 0.
        An alternate mapping 'BLANK' => 0 may be provided, allowing either
        'EMPTY' or 'BLANK' to be encoded as 0, but 0 will always be decoded
        as 'EMPTY'.

        Parameters:
            code_dict (dict): A dictionary of additional translation aliases.
            **codes: additional keyword-value translation alias pairs.
        """
        alt = dict(code_dict, **codes)
        alt_decode = {str(val): key for key, val in alt.items()}

        dup = self._code.keys() & alt.keys()
        if dup:
            raise ValueError(f"Alternate contains duplicate keys: {dup}")

        new_vals = alt_decode.keys() - self._decode.keys()
        if new_vals:
            raise ValueError(f"Alternate contains new values: {new_vals}")

        self._code.update(alt)
        alt_decode.update(self._decode)
        self._decode = alt_decode

    def encode(self, value):
        return self._code[value]

    def decode(self, value):
        return self._decode[str(value)]

    def keywords(self, *keywords: str) -> None:
        """
        Add keywords which will be recognized by this codec when
        :meth:`.encode_all()` or :meth:`.decode_all()` is called.

        Parameters:
            *keywords (str): List of keywords to associate to this codec
        """

        self._keys.update(keywords)

    def encodes(self, keyword: str) -> bool:
        return keyword in self._keys

    def range(self) -> Set[str]:
        return set(self._code)

# ==============================================================================
# Fuzzy Matching
# ==============================================================================

class FuzzyCodec(Codec):
    """
    A fuzzy-match codec

    This codec matches the value given to :meth:`.encode` against the set
    of expected inputs, and uses the best match from the expected inputs
    to determine the correct encoded value.

    Note:

        Unlike the :class:`~MapCodec` and :class:`~SimpleCodec`, the
        "encoded" values are passed as the keys of the mapping dictionary.

    Example::

        >>> codec = FuzzyCodec({'ABC': 'apple', 'DEF': 'banana', 'GHI': 'cherry'})
        >>> codec.encode('Bnana', warn)
        'DEF'
        >>> codec.decode('DEF')
        'banana'
    """

    def __init__(self, decode_mapping: Dict[str, str]):

        self._decode = decode_mapping
        self._encode = {value.casefold(): key
                        for key, val in self._decode.items()
                        for value in (key, val)}

    def encode(self, value: str) -> str:
        """
        Encode a value into an MHI serialization string

        A warning is generated if the given value is only an approximate
        match to the values in the encoding map.

        Parameters:
           value: the value to encode

        Returns:
            str: the encoded string
        """
        return self._encode_with(value, self._encode)

    def encode_to(self, value: str, active: Set[str]) -> str:
        """
        Encode a value into an MHI serialization string using a
        restricted set of possible output options.

        A warning is generated if the given value is only an approximate
        match to the values in the active set of the encoding map.

        Parameters:
            value: the value to encode
            active: a set of 'enabled' conversion codes

        Returns:
            str: the encoded string
        """

        mapping = {value.casefold(): key
                   for key, val in self._decode.items() if key in active
                   for value in (key, val)}
        return self._encode_with(value, mapping)

    def equivalent(self, code: str, active: Set[str]) -> Optional[str]:
        """
        If a value can ``encode_to()`` to multiple codes, distinguished by
        which codes are in the ``active`` set, then a code may be mapped
        to a different code with a different active set.
        """

        if code in active:
            return code

        value = self._decode[code].casefold()
        for key in active:
            if self._decode[key].casefold() == value:
                return key
        return None

    def decode(self, value: str) -> str:
        """
        Decode a value from an MHI serialization string

        Parameters:
           value (str): the value to decode

        Returns:
            the decoded value
        """

        return self._decode[value]

    def range(self) -> List[str]:
        """
        Returns the range of values that this codec will encode,
        as in, maybe passed to :meth:`.encode` and will
        be returned by  :meth:`.decode`.

        Returns:
            values which can be encoded by the codec.
        """
        return sorted(self._decode.values())

    def active_range(self, active: Set[str]) -> List[str]:
        """
        Returns the range of values that this codec will encode,
        as in, maybe passed to :meth:`.encode_to` and will
        be returned by  :meth:`.decode`.

        Parameters:
           active: a set of 'enabled' output values

        Returns:
            values which can be encoded by the codec.
        """
        return sorted(val
                      for key, val in self._decode.items() if key in active)

    def _encode_with(self, value: str, mapping: Dict[str, str]) -> str:
        matches = get_close_matches(value.casefold(), mapping, 1)
        if not matches:
            raise ValueError(f"Unable to encode {value}")
        code = mapping[matches[0]]
        decoded = self.decode(code)
        if value != code and value.casefold() != decoded.casefold():
            self._warn_fuzzy_match(value, decoded)
        return code

    def _warn_fuzzy_match(self, user_value: str, interpreted: str):
        msg = ("\n"
               f"      input value: {user_value!r}\n"
               f"   interpreted as: {interpreted!r}")
        warn(msg, FuzzyMatchWarning)

    def __repr__(self):
        args = ', '.join(f"{key}={val}" for key, val in self._decode.items())
        return f"FuzzyCodec({args})"
