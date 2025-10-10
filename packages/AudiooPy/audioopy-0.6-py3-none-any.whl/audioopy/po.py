# -*- coding: UTF-8 -*-
"""
:filename: audioopy.po.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Translation system based on gettext with po/mo files.

.. _This file was initially part of SPPAS: <https://sppas.org>
.. _This file is now part of AudiooPy:
..

    Copyright (C) 2024-2025  Brigitte Bigi, CNRS
    Laboratoire Parole et Langage, Aix-en-Provence, France

    Use of this software is governed by the GNU Affero Public License, version 3.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

"""

from __future__ import annotations
import sys
import gettext
import locale
import logging
import os

# ----------------------------------------------------------------------------


class textTranslate(object):
    """Fix the domain to translate messages and to activate the gettext method.

    The textTranslate class is designed to handle the translation of messages
    using the GNU gettext library. It sets up the translation environment based
    on the specified or default language and provides methods to translate
    messages and handle errors with appropriate translations.

    :Example:
    >>> # Create an instance of textTranslate with default language 'en'
    >>> translator = textTranslate()
    >>> # Get the translation object for the domain 'audioopy'
    >>> _ = textTranslate().translation().gettext
    >>> # Translate a message
    >>> my_string = _("Some string in the domain.")
    >>> # Handle an error message
    >>> error_message = translator.error(2000)
    >>> print(error_message)

    The locale is used to set the language; default value is 'en'.
    The path to search for a domain translation is the one of the 'po' folder
    of the 'audioopy' package.

    """

    def __init__(self, default_lang: str = "en"):
        """Create a textTranslate instance.

        Fields:

        - __po: Path to the 'po' folder containing the translation files.
        - __default: List containing the default language.
        - __lang: List of languages derived from the system's locale and the specified default language.

        :param default_lang: (str) The default language to fall back on

        """
        self.__po = os.path.join(os.path.dirname(os.path.abspath(__file__)), "po")
        self.__default = [default_lang]
        self.__lang = textTranslate.get_lang_list(default_lang)

    # ------------------------------------------------------------------------

    def translation(self, domain: str = "audioopy"):
        """Create the GNUTranslations for a given domain.

        A domain corresponds to a .po file of the language in the 'po' folder
        of the package.

        :param domain: (str) Name of the domain.
        :return: (GNUTranslations)

        """
        # Try to enable translation with the given domain and language
        t = self._install_translation(domain, self.__lang)
        if t is None:
            # Try with the default language
            t = self._install_translation(domain, self.__default)
        if t is not None:
            return t

        # No language installed. The messages won't be translated;
        # at least they are simply returned.
        return gettext.Catalog(domain, self.__po)

    # ------------------------------------------------------------------------

    def _install_translation(self, domain, languages):
        """Instantiate the GNUTranslations for a given domain."""
        try:
            t = gettext.translation(domain, self.__po, languages)
            t.install()
        except IOError:
            t = None

        return t

    # ------------------------------------------------------------------------

    @staticmethod
    def get_lang_list(default: str = "en") -> list:
        """Return the list of languages depending on the default locale.

        At a first stage, the language is fixed with the default locale.
        the given default language is then either appended to the list or used.

        :param default: (str) The default language.
        :return: (list) Installed languages.

        """
        lc = list()
        lc.append(default)
        try:
            if sys.version_info < (3, 6):
                # Only the locale is needed, not the returned encoding.
                sys_locale, _ = locale.getdefaultlocale()
            else:
                sys_locale, _ = locale.getlocale()
            if sys_locale is None:
                # Under macOS, the locale is defined differently compared to
                # other systems, then Python cannot capture a valid value.
                # So, try something else:
                sys_locale = os.getenv("LANG")

            if sys_locale is not None:
                if "_" in sys_locale:
                    sys_locale = sys_locale[:sys_locale.index("_")]
                lc.insert(0, sys_locale)
            else:
                logging.warning("The Operating System didn't defined a valid default locale.")
                logging.warning("It means that it assigns the language in a *** non-standard way ***.")
                logging.warning("This problem can be fixed by setting properly the 'LANG' "
                                "environment variable. See the documentation of your OS.")
                logging.warning("As a consequence, the language is set to its default value: "
                                "{:s}".format(lc[0]))

        except Exception as e:
            logging.error(f"Can't get the system default locale: {e}")

        return lc

    # ------------------------------------------------------------------------

    def error(self, msg: str | int) -> str:
        """Return the error message from gettext with its number.

        :param msg: (str or int) Error identifier
        :return: (str) Translated message or message

        """
        _msg_id = ":ERROR -1: "
        # Format the input message
        if isinstance(msg, int):
            # Create the "msg_id" string of the po files
            _msg_id = ":ERROR " + "{:04d}".format(msg) + ": "
            # Translate
            try:
                translation = self.translation()
                return _msg_id + translation.gettext(_msg_id)
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                return ":ERROR -1: " + str(msg)

        # Translate
        try:
            translation = self.translation()
            return _msg_id + translation.gettext(msg)
        except:
            return _msg_id + str(msg)

# ---------------------------------------------------------------------------


tt = textTranslate(default_lang="en")
