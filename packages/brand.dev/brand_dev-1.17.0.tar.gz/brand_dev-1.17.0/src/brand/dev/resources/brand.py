# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from ..types import (
    brand_ai_query_params,
    brand_prefetch_params,
    brand_retrieve_params,
    brand_screenshot_params,
    brand_styleguide_params,
    brand_retrieve_naics_params,
    brand_retrieve_simplified_params,
    brand_identify_from_transaction_params,
)
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.brand_ai_query_response import BrandAIQueryResponse
from ..types.brand_prefetch_response import BrandPrefetchResponse
from ..types.brand_retrieve_response import BrandRetrieveResponse
from ..types.brand_screenshot_response import BrandScreenshotResponse
from ..types.brand_styleguide_response import BrandStyleguideResponse
from ..types.brand_retrieve_naics_response import BrandRetrieveNaicsResponse
from ..types.brand_retrieve_simplified_response import BrandRetrieveSimplifiedResponse
from ..types.brand_identify_from_transaction_response import BrandIdentifyFromTransactionResponse

__all__ = ["BrandResource", "AsyncBrandResource"]


class BrandResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BrandResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/brand-dot-dev/python-sdk#accessing-raw-response-data-eg-headers
        """
        return BrandResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BrandResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/brand-dot-dev/python-sdk#with_streaming_response
        """
        return BrandResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        domain: str | Omit = omit,
        force_language: Literal[
            "albanian",
            "arabic",
            "azeri",
            "bengali",
            "bulgarian",
            "cebuano",
            "croatian",
            "czech",
            "danish",
            "dutch",
            "english",
            "estonian",
            "farsi",
            "finnish",
            "french",
            "german",
            "hausa",
            "hawaiian",
            "hindi",
            "hungarian",
            "icelandic",
            "indonesian",
            "italian",
            "kazakh",
            "kyrgyz",
            "latin",
            "latvian",
            "lithuanian",
            "macedonian",
            "mongolian",
            "nepali",
            "norwegian",
            "pashto",
            "pidgin",
            "polish",
            "portuguese",
            "romanian",
            "russian",
            "serbian",
            "slovak",
            "slovene",
            "somali",
            "spanish",
            "swahili",
            "swedish",
            "tagalog",
            "turkish",
            "ukrainian",
            "urdu",
            "uzbek",
            "vietnamese",
            "welsh",
        ]
        | Omit = omit,
        max_speed: bool | Omit = omit,
        name: str | Omit = omit,
        ticker: str | Omit = omit,
        ticker_exchange: Literal[
            "AMEX",
            "AMS",
            "AQS",
            "ASX",
            "ATH",
            "BER",
            "BME",
            "BRU",
            "BSE",
            "BUD",
            "BUE",
            "BVC",
            "CBOE",
            "CNQ",
            "CPH",
            "DFM",
            "DOH",
            "DUB",
            "DUS",
            "DXE",
            "EGX",
            "FSX",
            "HAM",
            "HEL",
            "HKSE",
            "HOSE",
            "ICE",
            "IOB",
            "IST",
            "JKT",
            "JNB",
            "JPX",
            "KLS",
            "KOE",
            "KSC",
            "KUW",
            "LIS",
            "LSE",
            "MCX",
            "MEX",
            "MIL",
            "MUN",
            "NASDAQ",
            "NEO",
            "NSE",
            "NYSE",
            "NZE",
            "OSL",
            "OTC",
            "PAR",
            "PNK",
            "PRA",
            "RIS",
            "SAO",
            "SAU",
            "SES",
            "SET",
            "SGO",
            "SHH",
            "SHZ",
            "SIX",
            "STO",
            "STU",
            "TAI",
            "TAL",
            "TLV",
            "TSX",
            "TSXV",
            "TWO",
            "VIE",
            "WSE",
            "XETRA",
        ]
        | Omit = omit,
        timeout_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandRetrieveResponse:
        """
        Retrieve brand information using one of three methods: domain name, company
        name, or stock ticker symbol. Exactly one of these parameters must be provided.

        Args:
          domain: Domain name to retrieve brand data for (e.g., 'example.com', 'google.com').
              Cannot be used with name or ticker parameters.

          force_language: Optional parameter to force the language of the retrieved brand data. Works with
              all three lookup methods.

          max_speed: Optional parameter to optimize the API call for maximum speed. When set to true,
              the API will skip time-consuming operations for faster response at the cost of
              less comprehensive data. Works with all three lookup methods.

          name: Company name to retrieve brand data for (e.g., 'Apple Inc', 'Microsoft
              Corporation'). Must be 3-30 characters. Cannot be used with domain or ticker
              parameters.

          ticker: Stock ticker symbol to retrieve brand data for (e.g., 'AAPL', 'GOOGL', 'BRK.A').
              Must be 1-15 characters, letters/numbers/dots only. Cannot be used with domain
              or name parameters.

          ticker_exchange: Optional stock exchange for the ticker. Only used when ticker parameter is
              provided. Defaults to assume ticker is American if not specified.

          timeout_ms: Optional timeout in milliseconds for the request. If the request takes longer
              than this value, it will be aborted with a 408 status code. Maximum allowed
              value is 300000ms (5 minutes).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/brand/retrieve",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "domain": domain,
                        "force_language": force_language,
                        "max_speed": max_speed,
                        "name": name,
                        "ticker": ticker,
                        "ticker_exchange": ticker_exchange,
                        "timeout_ms": timeout_ms,
                    },
                    brand_retrieve_params.BrandRetrieveParams,
                ),
            ),
            cast_to=BrandRetrieveResponse,
        )

    def ai_query(
        self,
        *,
        data_to_extract: Iterable[brand_ai_query_params.DataToExtract],
        domain: str,
        specific_pages: brand_ai_query_params.SpecificPages | Omit = omit,
        timeout_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandAIQueryResponse:
        """Beta feature: Use AI to extract specific data points from a brand's website.

        The
        AI will crawl the website and extract the requested information based on the
        provided data points.

        Args:
          data_to_extract: Array of data points to extract from the website

          domain: The domain name to analyze

          specific_pages: Optional object specifying which pages to analyze

          timeout_ms: Optional timeout in milliseconds for the request. If the request takes longer
              than this value, it will be aborted with a 408 status code. Maximum allowed
              value is 300000ms (5 minutes).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/brand/ai/query",
            body=maybe_transform(
                {
                    "data_to_extract": data_to_extract,
                    "domain": domain,
                    "specific_pages": specific_pages,
                    "timeout_ms": timeout_ms,
                },
                brand_ai_query_params.BrandAIQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrandAIQueryResponse,
        )

    def identify_from_transaction(
        self,
        *,
        transaction_info: str,
        timeout_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandIdentifyFromTransactionResponse:
        """
        Endpoint specially designed for platforms that want to identify transaction data
        by the transaction title.

        Args:
          transaction_info: Transaction information to identify the brand

          timeout_ms: Optional timeout in milliseconds for the request. If the request takes longer
              than this value, it will be aborted with a 408 status code. Maximum allowed
              value is 300000ms (5 minutes).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/brand/transaction_identifier",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "transaction_info": transaction_info,
                        "timeout_ms": timeout_ms,
                    },
                    brand_identify_from_transaction_params.BrandIdentifyFromTransactionParams,
                ),
            ),
            cast_to=BrandIdentifyFromTransactionResponse,
        )

    def prefetch(
        self,
        *,
        domain: str,
        timeout_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandPrefetchResponse:
        """
        Signal that you may fetch brand data for a particular domain soon to improve
        latency. This endpoint does not charge credits and is available for paid
        customers to optimize future requests. [You must be on a paid plan to use this
        endpoint]

        Args:
          domain: Domain name to prefetch brand data for

          timeout_ms: Optional timeout in milliseconds for the request. If the request takes longer
              than this value, it will be aborted with a 408 status code. Maximum allowed
              value is 300000ms (5 minutes).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/brand/prefetch",
            body=maybe_transform(
                {
                    "domain": domain,
                    "timeout_ms": timeout_ms,
                },
                brand_prefetch_params.BrandPrefetchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrandPrefetchResponse,
        )

    def retrieve_naics(
        self,
        *,
        input: str,
        timeout_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandRetrieveNaicsResponse:
        """
        Endpoint to classify any brand into a 2022 NAICS code.

        Args:
          input: Brand domain or title to retrieve NAICS code for. If a valid domain is provided
              in `input`, it will be used for classification, otherwise, we will search for
              the brand using the provided title.

          timeout_ms: Optional timeout in milliseconds for the request. If the request takes longer
              than this value, it will be aborted with a 408 status code. Maximum allowed
              value is 300000ms (5 minutes).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/brand/naics",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "input": input,
                        "timeout_ms": timeout_ms,
                    },
                    brand_retrieve_naics_params.BrandRetrieveNaicsParams,
                ),
            ),
            cast_to=BrandRetrieveNaicsResponse,
        )

    def retrieve_simplified(
        self,
        *,
        domain: str,
        timeout_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandRetrieveSimplifiedResponse:
        """
        Returns a simplified version of brand data containing only essential
        information: domain, title, colors, logos, and backdrops. This endpoint is
        optimized for faster responses and reduced data transfer.

        Args:
          domain: Domain name to retrieve simplified brand data for

          timeout_ms: Optional timeout in milliseconds for the request. If the request takes longer
              than this value, it will be aborted with a 408 status code. Maximum allowed
              value is 300000ms (5 minutes).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/brand/retrieve-simplified",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "domain": domain,
                        "timeout_ms": timeout_ms,
                    },
                    brand_retrieve_simplified_params.BrandRetrieveSimplifiedParams,
                ),
            ),
            cast_to=BrandRetrieveSimplifiedResponse,
        )

    def screenshot(
        self,
        *,
        domain: str,
        full_screenshot: Literal["true", "false"] | Omit = omit,
        page: Literal["login", "signup", "blog", "careers", "pricing", "terms", "privacy", "contact"] | Omit = omit,
        prioritize: Literal["speed", "quality"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandScreenshotResponse:
        """Beta feature: Capture a screenshot of a website.

        Supports both viewport
        (standard browser view) and full-page screenshots. Can also screenshot specific
        page types (login, pricing, etc.) by using heuristics to find the appropriate
        URL. Returns a URL to the uploaded screenshot image hosted on our CDN.

        Args:
          domain: Domain name to take screenshot of (e.g., 'example.com', 'google.com'). The
              domain will be automatically normalized and validated.

          full_screenshot: Optional parameter to determine screenshot type. If 'true', takes a full page
              screenshot capturing all content. If 'false' or not provided, takes a viewport
              screenshot (standard browser view).

          page: Optional parameter to specify which page type to screenshot. If provided, the
              system will scrape the domain's links and use heuristics to find the most
              appropriate URL for the specified page type (30 supported languages). If not
              provided, screenshots the main domain landing page.

          prioritize: Optional parameter to prioritize screenshot capture. If 'speed', optimizes for
              faster capture with basic quality. If 'quality', optimizes for higher quality
              with longer wait times. Defaults to 'quality' if not provided.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/brand/screenshot",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "domain": domain,
                        "full_screenshot": full_screenshot,
                        "page": page,
                        "prioritize": prioritize,
                    },
                    brand_screenshot_params.BrandScreenshotParams,
                ),
            ),
            cast_to=BrandScreenshotResponse,
        )

    def styleguide(
        self,
        *,
        domain: str,
        prioritize: Literal["speed", "quality"] | Omit = omit,
        timeout_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandStyleguideResponse:
        """
        Beta feature: Automatically extract comprehensive design system information from
        a brand's website including colors, typography, spacing, shadows, and UI
        components.

        Args:
          domain: Domain name to extract styleguide from (e.g., 'example.com', 'google.com'). The
              domain will be automatically normalized and validated.

          prioritize: Optional parameter to prioritize screenshot capture for styleguide extraction.
              If 'speed', optimizes for faster capture with basic quality. If 'quality',
              optimizes for higher quality with longer wait times. Defaults to 'quality' if
              not provided.

          timeout_ms: Optional timeout in milliseconds for the request. If the request takes longer
              than this value, it will be aborted with a 408 status code. Maximum allowed
              value is 300000ms (5 minutes).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/brand/styleguide",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "domain": domain,
                        "prioritize": prioritize,
                        "timeout_ms": timeout_ms,
                    },
                    brand_styleguide_params.BrandStyleguideParams,
                ),
            ),
            cast_to=BrandStyleguideResponse,
        )


class AsyncBrandResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBrandResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/brand-dot-dev/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncBrandResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBrandResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/brand-dot-dev/python-sdk#with_streaming_response
        """
        return AsyncBrandResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        domain: str | Omit = omit,
        force_language: Literal[
            "albanian",
            "arabic",
            "azeri",
            "bengali",
            "bulgarian",
            "cebuano",
            "croatian",
            "czech",
            "danish",
            "dutch",
            "english",
            "estonian",
            "farsi",
            "finnish",
            "french",
            "german",
            "hausa",
            "hawaiian",
            "hindi",
            "hungarian",
            "icelandic",
            "indonesian",
            "italian",
            "kazakh",
            "kyrgyz",
            "latin",
            "latvian",
            "lithuanian",
            "macedonian",
            "mongolian",
            "nepali",
            "norwegian",
            "pashto",
            "pidgin",
            "polish",
            "portuguese",
            "romanian",
            "russian",
            "serbian",
            "slovak",
            "slovene",
            "somali",
            "spanish",
            "swahili",
            "swedish",
            "tagalog",
            "turkish",
            "ukrainian",
            "urdu",
            "uzbek",
            "vietnamese",
            "welsh",
        ]
        | Omit = omit,
        max_speed: bool | Omit = omit,
        name: str | Omit = omit,
        ticker: str | Omit = omit,
        ticker_exchange: Literal[
            "AMEX",
            "AMS",
            "AQS",
            "ASX",
            "ATH",
            "BER",
            "BME",
            "BRU",
            "BSE",
            "BUD",
            "BUE",
            "BVC",
            "CBOE",
            "CNQ",
            "CPH",
            "DFM",
            "DOH",
            "DUB",
            "DUS",
            "DXE",
            "EGX",
            "FSX",
            "HAM",
            "HEL",
            "HKSE",
            "HOSE",
            "ICE",
            "IOB",
            "IST",
            "JKT",
            "JNB",
            "JPX",
            "KLS",
            "KOE",
            "KSC",
            "KUW",
            "LIS",
            "LSE",
            "MCX",
            "MEX",
            "MIL",
            "MUN",
            "NASDAQ",
            "NEO",
            "NSE",
            "NYSE",
            "NZE",
            "OSL",
            "OTC",
            "PAR",
            "PNK",
            "PRA",
            "RIS",
            "SAO",
            "SAU",
            "SES",
            "SET",
            "SGO",
            "SHH",
            "SHZ",
            "SIX",
            "STO",
            "STU",
            "TAI",
            "TAL",
            "TLV",
            "TSX",
            "TSXV",
            "TWO",
            "VIE",
            "WSE",
            "XETRA",
        ]
        | Omit = omit,
        timeout_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandRetrieveResponse:
        """
        Retrieve brand information using one of three methods: domain name, company
        name, or stock ticker symbol. Exactly one of these parameters must be provided.

        Args:
          domain: Domain name to retrieve brand data for (e.g., 'example.com', 'google.com').
              Cannot be used with name or ticker parameters.

          force_language: Optional parameter to force the language of the retrieved brand data. Works with
              all three lookup methods.

          max_speed: Optional parameter to optimize the API call for maximum speed. When set to true,
              the API will skip time-consuming operations for faster response at the cost of
              less comprehensive data. Works with all three lookup methods.

          name: Company name to retrieve brand data for (e.g., 'Apple Inc', 'Microsoft
              Corporation'). Must be 3-30 characters. Cannot be used with domain or ticker
              parameters.

          ticker: Stock ticker symbol to retrieve brand data for (e.g., 'AAPL', 'GOOGL', 'BRK.A').
              Must be 1-15 characters, letters/numbers/dots only. Cannot be used with domain
              or name parameters.

          ticker_exchange: Optional stock exchange for the ticker. Only used when ticker parameter is
              provided. Defaults to assume ticker is American if not specified.

          timeout_ms: Optional timeout in milliseconds for the request. If the request takes longer
              than this value, it will be aborted with a 408 status code. Maximum allowed
              value is 300000ms (5 minutes).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/brand/retrieve",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "domain": domain,
                        "force_language": force_language,
                        "max_speed": max_speed,
                        "name": name,
                        "ticker": ticker,
                        "ticker_exchange": ticker_exchange,
                        "timeout_ms": timeout_ms,
                    },
                    brand_retrieve_params.BrandRetrieveParams,
                ),
            ),
            cast_to=BrandRetrieveResponse,
        )

    async def ai_query(
        self,
        *,
        data_to_extract: Iterable[brand_ai_query_params.DataToExtract],
        domain: str,
        specific_pages: brand_ai_query_params.SpecificPages | Omit = omit,
        timeout_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandAIQueryResponse:
        """Beta feature: Use AI to extract specific data points from a brand's website.

        The
        AI will crawl the website and extract the requested information based on the
        provided data points.

        Args:
          data_to_extract: Array of data points to extract from the website

          domain: The domain name to analyze

          specific_pages: Optional object specifying which pages to analyze

          timeout_ms: Optional timeout in milliseconds for the request. If the request takes longer
              than this value, it will be aborted with a 408 status code. Maximum allowed
              value is 300000ms (5 minutes).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/brand/ai/query",
            body=await async_maybe_transform(
                {
                    "data_to_extract": data_to_extract,
                    "domain": domain,
                    "specific_pages": specific_pages,
                    "timeout_ms": timeout_ms,
                },
                brand_ai_query_params.BrandAIQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrandAIQueryResponse,
        )

    async def identify_from_transaction(
        self,
        *,
        transaction_info: str,
        timeout_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandIdentifyFromTransactionResponse:
        """
        Endpoint specially designed for platforms that want to identify transaction data
        by the transaction title.

        Args:
          transaction_info: Transaction information to identify the brand

          timeout_ms: Optional timeout in milliseconds for the request. If the request takes longer
              than this value, it will be aborted with a 408 status code. Maximum allowed
              value is 300000ms (5 minutes).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/brand/transaction_identifier",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "transaction_info": transaction_info,
                        "timeout_ms": timeout_ms,
                    },
                    brand_identify_from_transaction_params.BrandIdentifyFromTransactionParams,
                ),
            ),
            cast_to=BrandIdentifyFromTransactionResponse,
        )

    async def prefetch(
        self,
        *,
        domain: str,
        timeout_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandPrefetchResponse:
        """
        Signal that you may fetch brand data for a particular domain soon to improve
        latency. This endpoint does not charge credits and is available for paid
        customers to optimize future requests. [You must be on a paid plan to use this
        endpoint]

        Args:
          domain: Domain name to prefetch brand data for

          timeout_ms: Optional timeout in milliseconds for the request. If the request takes longer
              than this value, it will be aborted with a 408 status code. Maximum allowed
              value is 300000ms (5 minutes).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/brand/prefetch",
            body=await async_maybe_transform(
                {
                    "domain": domain,
                    "timeout_ms": timeout_ms,
                },
                brand_prefetch_params.BrandPrefetchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrandPrefetchResponse,
        )

    async def retrieve_naics(
        self,
        *,
        input: str,
        timeout_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandRetrieveNaicsResponse:
        """
        Endpoint to classify any brand into a 2022 NAICS code.

        Args:
          input: Brand domain or title to retrieve NAICS code for. If a valid domain is provided
              in `input`, it will be used for classification, otherwise, we will search for
              the brand using the provided title.

          timeout_ms: Optional timeout in milliseconds for the request. If the request takes longer
              than this value, it will be aborted with a 408 status code. Maximum allowed
              value is 300000ms (5 minutes).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/brand/naics",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "input": input,
                        "timeout_ms": timeout_ms,
                    },
                    brand_retrieve_naics_params.BrandRetrieveNaicsParams,
                ),
            ),
            cast_to=BrandRetrieveNaicsResponse,
        )

    async def retrieve_simplified(
        self,
        *,
        domain: str,
        timeout_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandRetrieveSimplifiedResponse:
        """
        Returns a simplified version of brand data containing only essential
        information: domain, title, colors, logos, and backdrops. This endpoint is
        optimized for faster responses and reduced data transfer.

        Args:
          domain: Domain name to retrieve simplified brand data for

          timeout_ms: Optional timeout in milliseconds for the request. If the request takes longer
              than this value, it will be aborted with a 408 status code. Maximum allowed
              value is 300000ms (5 minutes).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/brand/retrieve-simplified",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "domain": domain,
                        "timeout_ms": timeout_ms,
                    },
                    brand_retrieve_simplified_params.BrandRetrieveSimplifiedParams,
                ),
            ),
            cast_to=BrandRetrieveSimplifiedResponse,
        )

    async def screenshot(
        self,
        *,
        domain: str,
        full_screenshot: Literal["true", "false"] | Omit = omit,
        page: Literal["login", "signup", "blog", "careers", "pricing", "terms", "privacy", "contact"] | Omit = omit,
        prioritize: Literal["speed", "quality"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandScreenshotResponse:
        """Beta feature: Capture a screenshot of a website.

        Supports both viewport
        (standard browser view) and full-page screenshots. Can also screenshot specific
        page types (login, pricing, etc.) by using heuristics to find the appropriate
        URL. Returns a URL to the uploaded screenshot image hosted on our CDN.

        Args:
          domain: Domain name to take screenshot of (e.g., 'example.com', 'google.com'). The
              domain will be automatically normalized and validated.

          full_screenshot: Optional parameter to determine screenshot type. If 'true', takes a full page
              screenshot capturing all content. If 'false' or not provided, takes a viewport
              screenshot (standard browser view).

          page: Optional parameter to specify which page type to screenshot. If provided, the
              system will scrape the domain's links and use heuristics to find the most
              appropriate URL for the specified page type (30 supported languages). If not
              provided, screenshots the main domain landing page.

          prioritize: Optional parameter to prioritize screenshot capture. If 'speed', optimizes for
              faster capture with basic quality. If 'quality', optimizes for higher quality
              with longer wait times. Defaults to 'quality' if not provided.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/brand/screenshot",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "domain": domain,
                        "full_screenshot": full_screenshot,
                        "page": page,
                        "prioritize": prioritize,
                    },
                    brand_screenshot_params.BrandScreenshotParams,
                ),
            ),
            cast_to=BrandScreenshotResponse,
        )

    async def styleguide(
        self,
        *,
        domain: str,
        prioritize: Literal["speed", "quality"] | Omit = omit,
        timeout_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BrandStyleguideResponse:
        """
        Beta feature: Automatically extract comprehensive design system information from
        a brand's website including colors, typography, spacing, shadows, and UI
        components.

        Args:
          domain: Domain name to extract styleguide from (e.g., 'example.com', 'google.com'). The
              domain will be automatically normalized and validated.

          prioritize: Optional parameter to prioritize screenshot capture for styleguide extraction.
              If 'speed', optimizes for faster capture with basic quality. If 'quality',
              optimizes for higher quality with longer wait times. Defaults to 'quality' if
              not provided.

          timeout_ms: Optional timeout in milliseconds for the request. If the request takes longer
              than this value, it will be aborted with a 408 status code. Maximum allowed
              value is 300000ms (5 minutes).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/brand/styleguide",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "domain": domain,
                        "prioritize": prioritize,
                        "timeout_ms": timeout_ms,
                    },
                    brand_styleguide_params.BrandStyleguideParams,
                ),
            ),
            cast_to=BrandStyleguideResponse,
        )


class BrandResourceWithRawResponse:
    def __init__(self, brand: BrandResource) -> None:
        self._brand = brand

        self.retrieve = to_raw_response_wrapper(
            brand.retrieve,
        )
        self.ai_query = to_raw_response_wrapper(
            brand.ai_query,
        )
        self.identify_from_transaction = to_raw_response_wrapper(
            brand.identify_from_transaction,
        )
        self.prefetch = to_raw_response_wrapper(
            brand.prefetch,
        )
        self.retrieve_naics = to_raw_response_wrapper(
            brand.retrieve_naics,
        )
        self.retrieve_simplified = to_raw_response_wrapper(
            brand.retrieve_simplified,
        )
        self.screenshot = to_raw_response_wrapper(
            brand.screenshot,
        )
        self.styleguide = to_raw_response_wrapper(
            brand.styleguide,
        )


class AsyncBrandResourceWithRawResponse:
    def __init__(self, brand: AsyncBrandResource) -> None:
        self._brand = brand

        self.retrieve = async_to_raw_response_wrapper(
            brand.retrieve,
        )
        self.ai_query = async_to_raw_response_wrapper(
            brand.ai_query,
        )
        self.identify_from_transaction = async_to_raw_response_wrapper(
            brand.identify_from_transaction,
        )
        self.prefetch = async_to_raw_response_wrapper(
            brand.prefetch,
        )
        self.retrieve_naics = async_to_raw_response_wrapper(
            brand.retrieve_naics,
        )
        self.retrieve_simplified = async_to_raw_response_wrapper(
            brand.retrieve_simplified,
        )
        self.screenshot = async_to_raw_response_wrapper(
            brand.screenshot,
        )
        self.styleguide = async_to_raw_response_wrapper(
            brand.styleguide,
        )


class BrandResourceWithStreamingResponse:
    def __init__(self, brand: BrandResource) -> None:
        self._brand = brand

        self.retrieve = to_streamed_response_wrapper(
            brand.retrieve,
        )
        self.ai_query = to_streamed_response_wrapper(
            brand.ai_query,
        )
        self.identify_from_transaction = to_streamed_response_wrapper(
            brand.identify_from_transaction,
        )
        self.prefetch = to_streamed_response_wrapper(
            brand.prefetch,
        )
        self.retrieve_naics = to_streamed_response_wrapper(
            brand.retrieve_naics,
        )
        self.retrieve_simplified = to_streamed_response_wrapper(
            brand.retrieve_simplified,
        )
        self.screenshot = to_streamed_response_wrapper(
            brand.screenshot,
        )
        self.styleguide = to_streamed_response_wrapper(
            brand.styleguide,
        )


class AsyncBrandResourceWithStreamingResponse:
    def __init__(self, brand: AsyncBrandResource) -> None:
        self._brand = brand

        self.retrieve = async_to_streamed_response_wrapper(
            brand.retrieve,
        )
        self.ai_query = async_to_streamed_response_wrapper(
            brand.ai_query,
        )
        self.identify_from_transaction = async_to_streamed_response_wrapper(
            brand.identify_from_transaction,
        )
        self.prefetch = async_to_streamed_response_wrapper(
            brand.prefetch,
        )
        self.retrieve_naics = async_to_streamed_response_wrapper(
            brand.retrieve_naics,
        )
        self.retrieve_simplified = async_to_streamed_response_wrapper(
            brand.retrieve_simplified,
        )
        self.screenshot = async_to_streamed_response_wrapper(
            brand.screenshot,
        )
        self.styleguide = async_to_streamed_response_wrapper(
            brand.styleguide,
        )
