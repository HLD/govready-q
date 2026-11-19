"""CSRF failure handling (settings.CSRF_FAILURE_VIEW)."""

from django.contrib import messages
from django.middleware.csrf import REASON_NO_CSRF_COOKIE
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.csrf import csrf_failure as django_csrf_failure


def csrf_failure(request, reason=""):
    """Let users retry a form whose CSRF token went stale, instead of showing a bare 403.

    Signing in issues a new CSRF secret. When two requests sign the same browser in
    at once (e.g. a prefetch alongside the page load after a single sign-on
    redirect), or a form is resubmitted from the back/forward cache, the page's
    token no longer matches the browser's cookie. For an ordinary form POST that
    failed only because of a stale or missing token, send the user back to the page
    (re-rendered with a fresh token) with a message asking them to try again. The
    rejected POST was not processed.

    Everything else gets Django's usual 403: Origin/Referer failures (possible
    cross-site requests), AJAX requests, and referrers that are not this site.
    """
    token_problem = reason == REASON_NO_CSRF_COOKIE or reason.startswith("CSRF token")
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    referer = request.META.get("HTTP_REFERER", "")
    same_site_referer = url_has_allowed_host_and_scheme(
        referer, allowed_hosts={request.get_host()}, require_https=request.is_secure())
    if request.method == "POST" and token_problem and not is_ajax and same_site_referer:
        messages.warning(request, "Your session was refreshed, so that form could not be submitted. Please try again.")
        return redirect(referer)
    return django_csrf_failure(request, reason=reason)
