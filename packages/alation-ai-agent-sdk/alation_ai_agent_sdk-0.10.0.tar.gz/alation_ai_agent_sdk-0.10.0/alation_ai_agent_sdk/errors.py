from http import HTTPStatus


class AlationAPIError(Exception):
    """Raised when an Alation API call fails logically or at HTTP level."""

    def __init__(
        self,
        message: str,
        *,
        original_exception=None,
        status_code=None,
        response_body=None,
        reason=None,
        resolution_hint=None,
        help_links=None,
        alation_release_name=None,
        dist_version=None,
        is_retryable=None,
    ):
        super().__init__(message)
        self.original_exception = original_exception
        self.status_code = status_code
        self.response_body = response_body
        self.reason = reason
        self.resolution_hint = resolution_hint
        self.help_links = help_links or []
        self.alation_release_name = alation_release_name
        self.dist_version = dist_version
        self.is_retryable = is_retryable
        if self.is_retryable is None and status_code is not None:
            self.is_retryable = status_code in [
                HTTPStatus.TOO_MANY_REQUESTS,
                HTTPStatus.INTERNAL_SERVER_ERROR,
            ]

    def to_dict(self) -> dict:
        return {
            "message": str(self),
            "status_code": self.status_code,
            "reason": self.reason,
            "resolution_hint": self.resolution_hint,
            "is_retryable": self.is_retryable,
            "response_body": self.response_body,
            "help_links": self.help_links,
            "alation_release_name": self.alation_release_name,
            "dist_version": self.dist_version,
        }


class AlationErrorClassifier:
    @staticmethod
    def classify_catalog_error(status_code: int, response_body: dict) -> dict:
        # If the response body has 'error' and 'message', use them directly
        if isinstance(response_body, dict):
            error_code = response_body.get("error")
            error_message = response_body.get("message")
            if error_code and error_message:
                return {
                    "reason": error_code,
                    "resolution_hint": error_message,
                    "help_links": [],
                }

        # Fallback: use generic error handling by status code
        reason = "Unexpected Error"
        resolution_hint = "An unknown error occurred."
        help_links = []
        is_retryable = None

        if status_code == HTTPStatus.BAD_REQUEST:
            reason = "Bad Request"
            resolution_hint = (
                response_body.get("error")
                or response_body.get("message")
                or "Request was malformed. Check the query and signature structure."
            )
            help_links = [
                "https://developer.alation.com/dev/docs/customize-the-aggregated-context-api-calls-with-a-signature",
                "https://github.com/Alation/alation-ai-agent-sdk?tab=readme-ov-file#usage",
            ]
        elif status_code == HTTPStatus.UNAUTHORIZED:
            reason = "Unauthorized"
            resolution_hint = "Token missing or invalid. Retry with a valid token."
            help_links = [
                "https://developer.alation.com/dev/v2024.1/docs/authentication-into-alation-apis",
                "https://developer.alation.com/dev/reference/refresh-access-token-overview",
            ]
        elif status_code == HTTPStatus.FORBIDDEN:
            reason = "Forbidden"
            resolution_hint = "Token likely expired or lacks permissions. Ask the user to re-authenticate."
            help_links = [
                "https://developer.alation.com/dev/v2024.1/docs/authentication-into-alation-apis",
                "https://developer.alation.com/dev/reference/refresh-access-token-overview",
            ]
        elif status_code == HTTPStatus.NOT_FOUND:
            reason = "Not Found"
            resolution_hint = "The requested resource was not found or is not enabled, check feature flag."
            help_links = [
                "https://developer.alation.com/dev/docs/guide-to-aggregated-context-api-beta"
            ]
        elif status_code == HTTPStatus.TOO_MANY_REQUESTS:
            if AlationErrorClassifier._is_quota_error(status_code, response_body):
                reason = "License Quota Exceeded"
                resolution_hint = (
                    "Quota exhausted. Contact your Account Manager for pricing options."
                )
                help_links = [
                    "https://developer.alation.com/dev/docs/guide-to-aggregated-context-api-beta#overview",
                ]
                is_retryable = False
            else:
                reason = "Too Many Requests"
                resolution_hint = (
                    "Too many requests in a short time. Retry after some time."
                )
                help_links = [
                    "https://developer.alation.com/dev/docs/guide-to-aggregated-context-api-beta#rate-limiting",
                ]
                is_retryable = True
        elif status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
            reason = "Internal Server Error"
            resolution_hint = "Server error. Retry later or contact Alation support."
            help_links = [
                "https://developer.alation.com/dev/docs/guide-to-aggregated-context-api-beta"
            ]

        return {
            "reason": reason,
            "resolution_hint": resolution_hint,
            "help_links": help_links,
            "is_retryable": is_retryable,
        }

    @staticmethod
    def classify_token_error(status_code: int, response_body: dict) -> dict:
        reason = "Unexpected Token Error"
        resolution_hint = "An unknown token-related error occurred."
        help_links = [
            "https://developer.alation.com/dev/v2024.1/docs/authentication-into-alation-apis",
            "https://developer.alation.com/dev/reference/refresh-access-token-overview",
        ]

        if status_code == HTTPStatus.BAD_REQUEST:
            reason = "Token Request Invalid"
            resolution_hint = (
                response_body.get("error") or "Token request payload is malformed."
            )
        elif status_code == HTTPStatus.UNAUTHORIZED:
            reason = "Token Unauthorized"
            resolution_hint = (
                "[User ID,refresh token] or [client id, client secret] is invalid."
            )
        elif status_code == HTTPStatus.FORBIDDEN:
            reason = "Token Forbidden"
            resolution_hint = "You do not have permission to generate a token."
        elif status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
            reason = "Token Generation Failed"
            resolution_hint = "Alation server failed to process token request. Retry later or contact Alation support."

        return {
            "reason": reason,
            "resolution_hint": resolution_hint,
            "help_links": help_links,
        }

    @staticmethod
    def _is_quota_error(status_code: int, response_body: dict) -> bool:
        """Check if the error is related to quota limits."""
        return (
            status_code == HTTPStatus.TOO_MANY_REQUESTS
            and "entitlement" in response_body.get("error", "").lower()
        )
