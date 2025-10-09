import asyncio
import copy
import json
import os

from forwardbasespawner.utils import check_custom_scopes
from jupyterhub.apihandlers import APIHandler
from jupyterhub.apihandlers import default_handlers
from jupyterhub.utils import token_authenticated
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest


_outpost_flavors_cache = {}


async def get_user_specific_flavors(log, user_specific_flavor_systems={}):
    # This function can be used in authenticator.post_auth_hook to add user specific flavors
    # Systems may have user specific flavors
    # If that's the case we will send a request to the outpost, to
    # receive the allowed flavors for this specific user
    # user_specific_flavor_systems = {
    #   "system_name": {
    #     "url": "http://outpost.svc:8000/flavors",
    #     "body": ... # dict containing information that should be used by the Outpost
    #     "headers": ... # dict used for authenticating
    #     "request_kwargs": ... # optional, default: request_timeout: 2
    #   }
    # }

    ret = _outpost_flavors_cache
    tasks = []
    http_client = AsyncHTTPClient(
        force_instance=True, defaults=dict(validate_cert=False)
    )
    system_names = []
    for system_name, system_infos in user_specific_flavor_systems.items():
        url = system_infos.get("url", "No Url configured")
        headers = system_infos.get("headers", {})
        body = system_infos.get("body", {})
        log.info(
            f"OutpostFlavors user specific - Retrieve flavors from {system_name} / {url}"
        )
        request_kwargs = {"request_timeout": 2}
        request_kwargs.update(system_infos.get("request_kwargs", {}))
        req = HTTPRequest(
            url,
            method="POST",
            headers=headers,
            body=json.dumps(body),
            **request_kwargs,
        )
        tasks.append(http_client.fetch(req, raise_error=False))
        system_names.append(system_name)
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        names_results = list(zip(system_names, results))
        for name_result in names_results:
            try:
                if name_result[1].code == 200:
                    log.debug(
                        f"OutpostFlavors user specific - {name_result[0]} successful"
                    )
                    result_json = json.loads(name_result[1].body)
                    ret[name_result[0]] = result_json
                else:
                    log.warning(
                        f"OutpostFlavors user specific - {name_result[0]} - Answered with {name_result[1].code} ({name_result[1]})"
                    )
            except:
                log.exception(
                    f"OutpostFlavors user specific - {name_result.get(0, 'unknown')} Could not load result into json"
                )
    except:
        log.exception("OutpostFlavors user specific - Could not load get flavors")
    return ret


async def async_get_flavors(log, user=None):
    global _outpost_flavors_cache
    try:
        initial_system_names = os.environ.get("OUTPOST_FLAVOR_INITIAL_SYSTEM_NAMES", "")
        initial_system_urls = os.environ.get("OUTPOST_FLAVOR_INITIAL_SYSTEM_URLS", "")
        initial_system_tokens = os.environ.get(
            "OUTPOST_FLAVOR_INITIAL_SYSTEM_TOKENS", ""
        )

        # If initial checks are configured
        if initial_system_names and initial_system_urls:
            initial_system_names_list_all = initial_system_names.split(";")
            initial_system_urls_list_all = initial_system_urls.split(";")
            initial_system_tokens_list_all = initial_system_tokens.split(";")

            initial_system_names_list = []
            initial_system_urls_list = []
            initial_system_tokens_list = []
            i = 0
            # Only check for initial checks, when they're not yet part of _outpost_flavors_cache
            for system_name in initial_system_names_list_all:
                if system_name not in _outpost_flavors_cache.keys():
                    initial_system_names_list.append(system_name)
                    initial_system_urls_list.append(initial_system_urls_list_all[i])
                    initial_system_tokens_list.append(initial_system_tokens_list_all[i])
                i += 1

            # If systems are left without successful initial check, try to reach the Outpost
            if initial_system_names_list:
                log.info(
                    f"OutpostFlavors - Connect to {initial_system_names_list} / {initial_system_urls_list}"
                )

                urls_tokens = list(
                    zip(initial_system_urls_list, initial_system_tokens_list)
                )
                # use pycurl, if available:
                http_client = None
                try:
                    from tornado.curl_httpclient import CurlAsyncHTTPClient

                    http_client = CurlAsyncHTTPClient(
                        defaults=dict(validate_cert=False)
                    )
                except ImportError as e:
                    log.debug(
                        "Could not load pycurl: %s\npycurl is recommended if you have a large number of users.",
                        e,
                    )
                    http_client = AsyncHTTPClient(
                        force_instance=True, defaults=dict(validate_cert=False)
                    )
                tasks = []
                for url_token in urls_tokens:
                    req = HTTPRequest(
                        url_token[0],
                        headers={"Authorization": f"Basic {url_token[1]}"},
                        request_timeout=1,
                    )
                    tasks.append(http_client.fetch(req, raise_error=False))
                try:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    names_results = list(zip(initial_system_names_list, results))
                    for name_result in names_results:
                        if name_result[1].code == 200:
                            try:
                                log.info(
                                    f"OutpostFlavors - {name_result[0]} successful"
                                )
                                result_json = json.loads(name_result[1].body)
                                _outpost_flavors_cache[name_result[0]] = result_json
                            except:
                                log.exception(
                                    f"OutpostFlavors - {name_result[0]} Could not load result into json"
                                )
                        else:
                            log.warning(
                                f"OutpostFlavors - {name_result[0]} - Answered with {name_result[1].code}"
                            )
                except:
                    log.exception("OutpostFlavors failed, return empty dict")
    except:
        log.exception("OutpostFlavors failed, return empty dict")

    # If it's an user authenticated request, we override the available flavors, if
    # there's a dict with available flavors in auth_state.
    # One can add this in Authenticator.post_auth_hook, to allow user-specific
    # flavors for each Outpost.
    if user:
        auth_state = await user.get_auth_state()
        if auth_state:
            user_specific_flavors = auth_state.get("outpost_flavors", {})
            if user_specific_flavors:
                # Do not override global default flavors cache
                user_specific_ret = copy.deepcopy(_outpost_flavors_cache)
                for system_name, system_flavors in user_specific_flavors.items():
                    if type(system_flavors) == bool and not system_flavors:
                        # System is not allowed for this user
                        if system_name in user_specific_ret.keys():
                            del user_specific_ret[system_name]
                    elif type(system_flavors) == dict:
                        # Replace the default flavor dict with the user specific one
                        # but keep the "current" value
                        user_specific_ret[system_name] = system_flavors
                        for key, value in system_flavors.items():
                            specific_current = value.get("current", 0)
                            user_specific_ret[system_name][key]["current"] = (
                                _outpost_flavors_cache.get(system_name, {})
                                .get(key, {})
                                .get("current", specific_current)
                            )
                return user_specific_ret
    return _outpost_flavors_cache


class OutpostFlavorsAPIHandler(APIHandler):
    required_scopes = ["custom:outpostflavors:set"]

    def check_xsrf_cookie(self):
        pass

    @token_authenticated
    async def post(self, outpost_name):
        check_custom_scopes(self)
        global _outpost_flavors_cache

        body = self.request.body.decode("utf8")
        try:
            flavors = json.loads(body) if body else {}
        except:
            self.set_status(400)
            self.log.exception(
                f"{outpost_name} - Could not load body into json. Body: {body}"
            )
            return

        _outpost_flavors_cache[outpost_name] = flavors
        self.set_status(200)

    async def get(self):
        ret = await async_get_flavors(self.log, self.current_user)
        self.write(json.dumps(ret))
        self.set_status(200)
        return


default_handlers.append((r"/api/outpostflavors/([^/]+)", OutpostFlavorsAPIHandler))
default_handlers.append((r"/api/outpostflavors", OutpostFlavorsAPIHandler))
