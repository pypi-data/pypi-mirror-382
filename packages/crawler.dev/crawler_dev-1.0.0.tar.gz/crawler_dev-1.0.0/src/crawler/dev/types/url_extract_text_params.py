# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["URLExtractTextParams"]


class URLExtractTextParams(TypedDict, total=False):
    url: Required[str]
    """The URL to extract text from."""

    clean_text: bool
    """Whether to clean extracted text"""

    render_js: bool
    """Whether to render JavaScript for HTML content.

    This parameter is ignored for binary content types (PDF, DOC, etc.) since they
    are not HTML.
    """

    strip_boilerplate: bool
    """Whether to remove boilerplate text"""
