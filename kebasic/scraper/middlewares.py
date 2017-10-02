# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import re
from random import choice

from scrapy import log
from scrapy import signals
from scrapy.exceptions import NotConfigured, IgnoreRequest


class RotateUserAgentMiddleware(object):
    """Rotate user-agent for each request."""

    def __init__(self, user_agents):
        self.enabled = False
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        user_agents = crawler.settings.get('USER_AGENTS', [])

        if not user_agents:
            raise NotConfigured("USER_AGENTS not set or empty")

        o = cls(user_agents)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)

        return o

    def spider_opened(self, spider):
        self.enabled = getattr(spider, 'rotate_user_agent', self.enabled)

    def process_request(self, request, spider):
        if not self.enabled or not self.user_agents:
            return

        request.headers['user-agent'] = choice(self.user_agents)


class FilterResponsesMiddleware(object):
    """Limit the HTTP response types that Scrapy downloads."""

    @staticmethod
    def is_valid_response(type_whitelist, content_type_header):
        for type_regex in type_whitelist:
            if re.search(type_regex, content_type_header):
                return True
        return False

    def process_response(self, request, response, spider):
        """
        Only allow HTTP response types that that match the given list of
        filtering regexs
        """
        # each spider must define the variable response_type_whitelist as an
        # iterable of regular expressions. ex. (r'text', )
        type_whitelist = getattr(spider, "response_type_whitelist", None)
        content_type_header = response.headers.get('content-type', None)
        if not type_whitelist:
            return response
        elif not content_type_header:
            log.msg("no content type header: {}".format(response.url), level=log.DEBUG, spider=spider)
            raise IgnoreRequest()
        elif self.is_valid_response(type_whitelist, content_type_header):
            log.msg("valid response {}".format(response.url), level=log.DEBUG, spider=spider)
            return response
        else:
            msg = "Ignoring request {}, content-type was not in whitelist".format(response.url)
            log.msg(msg, level=log.DEBUG, spider=spider)
            raise IgnoreRequest()
