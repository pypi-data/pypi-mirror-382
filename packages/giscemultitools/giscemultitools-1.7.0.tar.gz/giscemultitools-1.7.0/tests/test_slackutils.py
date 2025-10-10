# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
import unittest

try:  # pragma: no cover - compatibility shim
    from unittest import mock
except ImportError:  # pragma: no cover
    import mock  # type: ignore

from giscemultitools.slackutils.utils import SlackUtils


class SlackUtilsNotifyTests(unittest.TestCase):
    @mock.patch('requests.post')
    def test_notify_posts_payload_to_each_hook(self, mock_post):
        SlackUtils.notify('https://hook.one, https://hook.two', 'payload')

        self.assertEqual(mock_post.call_count, 2)
        mock_post.assert_any_call('https://hook.one', data='payload', headers={'Content-type': 'application/json'})
        mock_post.assert_any_call('https://hook.two', data='payload', headers={'Content-type': 'application/json'})

    @mock.patch('requests.post')
    def test_notify_noops_when_no_hooks(self, mock_post):
        SlackUtils.notify('', 'payload')
        SlackUtils.notify(None, 'payload')

        mock_post.assert_not_called()


class SlackUtilsPayloadTests(unittest.TestCase):
    def test_generic_notify_data_returns_serialised_blocks(self):
        payload = SlackUtils.generic_notify_data(
            title='Deployment Finished',
            icon=':rocket:',
            message='All systems go',
            origin='automation'
        )

        data = json.loads(payload)
        self.assertIn('blocks', data)
        header = data['blocks'][0]
        self.assertEqual(header['type'], 'header')
        self.assertTrue(data['blocks'][2]['text']['text'].startswith('All systems go'))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
