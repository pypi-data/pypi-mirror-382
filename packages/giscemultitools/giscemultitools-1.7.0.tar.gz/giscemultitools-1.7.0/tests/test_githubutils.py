# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
from collections import OrderedDict

try:  # pragma: no cover - compatibility shim
    from unittest import mock
except ImportError:  # pragma: no cover
    import mock  # type: ignore

from giscemultitools.githubutils.utils import GithubUtils


class GithubUtilsPlainResponseTests(unittest.TestCase):
    def test_plain_get_commits_sha_from_merge_commit_formats_payload(self):
        response = {
            'data': {
                'repository': {
                    'pullRequest': {
                        'commits': {
                            'nodes': [
                                {'commit': {'oid': 'c1'}},
                                {'commit': {'oid': 'c2'}},
                            ]
                        },
                        'id': 'pr-id',
                        'number': 42,
                        'state': 'MERGED',
                        'milestone': {'title': 'Sprint 1'},
                        'url': 'https://example/pr/42',
                        'title': 'Add feature',
                        'baseRefName': 'main',
                        'mergedAt': '2023-02-02T00:00:00Z',
                        'createdAt': '2023-01-31T00:00:00Z',
                        'labels': {'nodes': [{'name': 'core'}]},
                        'projectItems': {
                            'nodes': [
                                {
                                    'project': {
                                        'title': 'Growth',
                                        'id': 'proj-1',
                                        'url': 'https://example/proj'
                                    },
                                    'id': 'card-1',
                                    'fieldValues': {
                                        'nodes': [
                                            None,
                                            {
                                                'name': 'In Progress',
                                                'id': 'status-id',
                                                'field': {
                                                    'id': 'field-id',
                                                    'name': 'Status',
                                                    'options': [
                                                        {'name': 'In Progress', 'id': 'opt-progress'}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }

        result = GithubUtils.plain_get_commits_sha_from_merge_commit(response)

        self.assertEqual(result['commits'], ['c1', 'c2'])
        self.assertEqual(result['pullRequest']['milestone'], 'Sprint 1')
        self.assertEqual(result['pullRequest']['labels'], [{'name': 'core'}])
        self.assertEqual(result['projectItems'][0]['project_name'], 'Growth')
        self.assertEqual(result['projectItems'][0]['card_state'], 'In Progress')
        self.assertIn('opt-progress', result['projectItems'][0]['field_column_options'].values())


class GithubUtilsRequesterTests(unittest.TestCase):
    @mock.patch('giscemultitools.githubutils.objects.GHAPIRequester')
    def test_get_pr_from_sha_merge_commit_returns_number(self, mock_requester_cls):
        mock_requester = mock_requester_cls.return_value
        mock_requester.get_pulls_from_sha.return_value = [
            {'merge_commit_sha': 'abc', 'number': 17},
            {'merge_commit_sha': 'def', 'number': 23},
        ]

        number = GithubUtils.get_pr_from_sha_merge_commit('gisce', 'erp', 'abc')

        self.assertEqual(number, 17)
        mock_requester_cls.assert_called_once_with('gisce', 'erp')
        mock_requester.get_pulls_from_sha.assert_called_once_with('abc')

    @mock.patch('giscemultitools.githubutils.objects.GHAPIRequester')
    def test_get_pr_from_sha_merge_commit_raises_when_missing(self, mock_requester_cls):
        mock_requester = mock_requester_cls.return_value
        mock_requester.get_pulls_from_sha.return_value = [
            {'merge_commit_sha': 'def', 'number': 23},
        ]

        with self.assertRaises(AssertionError):
            GithubUtils.get_pr_from_sha_merge_commit('gisce', 'erp', 'missing')

    @mock.patch('giscemultitools.githubutils.objects.GHAPIRequester')
    def test_get_commits_sha_from_merge_commit_formats_data(self, mock_requester_cls):
        mock_requester = mock_requester_cls.return_value
        mock_requester.get_pulls_from_sha.return_value = [
            {'merge_commit_sha': 'abc', 'number': 17}
        ]
        mock_requester.get_pull_request_projects_and_commits.return_value = {'graph': 'data'}
        with mock.patch.object(
            GithubUtils,
            'plain_get_commits_sha_from_merge_commit',
            return_value={'pullRequest': {'number': 17}}
        ) as plain_mock:
            result = GithubUtils.get_commits_sha_from_merge_commit('gisce', 'erp', 'abc')

        self.assertEqual(result['pullRequest']['number'], 17)
        plain_mock.assert_called_once_with({'graph': 'data'})

    @mock.patch('giscemultitools.githubutils.objects.GHAPIRequester')
    def test_get_pullrequest_info_uses_plain_formatter(self, mock_requester_cls):
        mock_requester = mock_requester_cls.return_value
        mock_requester.get_pull_request_projects_and_commits.return_value = {'graph': 'data'}
        with mock.patch.object(
            GithubUtils,
            'plain_get_commits_sha_from_merge_commit',
            return_value={'pullRequest': {'number': 20}}
        ) as plain_mock:
            result = GithubUtils.get_pullrequest_info('gisce', 'erp', 20)

        self.assertEqual(result['pullRequest']['number'], 20)
        plain_mock.assert_called_once_with({'graph': 'data'})

    @mock.patch('giscemultitools.githubutils.objects.GHAPIRequester')
    def test_get_pulls_from_project_and_column_aggregates_states(self, mock_requester_cls):
        mock_requester = mock_requester_cls.return_value
        mock_requester.get_pulls_from_project.side_effect = [
            ['merged-pr'],
            ['open-pr'],
        ]

        pulls = GithubUtils.get_pulls_from_project_and_column('gisce', 'erp', 'Project', 'In Progress')

        self.assertEqual(pulls, ['merged-pr', 'open-pr'])
        self.assertEqual(mock_requester.get_pulls_from_project.call_count, 2)


class GithubUtilsChecksTests(unittest.TestCase):
    def _build_context_payload(self, with_status=True):
        commit_payload = {'status': {'contexts': []}}
        if with_status:
            commit_payload['status']['contexts'] = [
                {
                    'context': 'ci/build',
                    'state': 'SUCCESS',
                    'targetUrl': 'https://ci/build'
                },
                {
                    'context': None,
                    'state': 'FAILURE',
                    'targetUrl': 'https://ci/missing'
                }
            ]
        return {
            'data': {
                'repository': {
                    'pullRequest': {
                        'commits': {
                            'nodes': [
                                {'commit': commit_payload}
                            ]
                        }
                    }
                }
            }
        }

    @mock.patch('giscemultitools.githubutils.objects.GHAPIRequester')
    def test_get_pullrequest_context_checks_filters_invalid_entries(self, mock_requester_cls):
        mock_requester = mock_requester_cls.return_value
        mock_requester.get_pr_checks.return_value = self._build_context_payload()

        result = GithubUtils.get_pullrequest_context_checks('gisce', 'erp', 10)

        self.assertEqual(result, [
            {
                'name': 'ci/build',
                'conclusion': 'SUCCESS',
                'permalink': 'https://ci/build'
            }
        ])

    @mock.patch('giscemultitools.githubutils.objects.GHAPIRequester')
    def test_get_pullrequest_context_checks_handles_absent_status(self, mock_requester_cls):
        mock_requester = mock_requester_cls.return_value
        payload = self._build_context_payload(with_status=False)
        payload['data']['repository']['pullRequest']['commits']['nodes'][0]['commit'].pop('status')
        mock_requester.get_pr_checks.return_value = payload

        result = GithubUtils.get_pullrequest_context_checks('gisce', 'erp', 10)

        self.assertEqual(result, [])

    @mock.patch('giscemultitools.githubutils.utils.GithubUtils.get_pullrequest_context_checks')
    def test_get_pullrequest_context_check_status_returns_matching(self, mock_context_checks):
        mock_context_checks.return_value = [
            {'name': 'ci/build', 'conclusion': 'SUCCESS'}
        ]

        status = GithubUtils.get_pullrequest_context_check_status('gisce', 'erp', 10, 'ci/build')

        self.assertEqual(status, 'SUCCESS')

    @mock.patch('giscemultitools.githubutils.utils.GithubUtils.get_pullrequest_context_checks')
    def test_get_pullrequest_context_check_status_raises_when_missing(self, mock_context_checks):
        mock_context_checks.return_value = []

        with self.assertRaises(AssertionError):
            GithubUtils.get_pullrequest_context_check_status('gisce', 'erp', 10, 'ci/test')

    def _build_checks_payload(self):
        return {
            'data': {
                'repository': {
                    'pullRequest': {
                        'commits': {
                            'nodes': [
                                {
                                    'commit': {
                                        'checkSuites': {
                                            'nodes': [
                                                {
                                                    'checkRuns': {
                                                        'nodes': [
                                                            {
                                                                'name': 'lint',
                                                                'conclusion': 'SUCCESS'
                                                            },
                                                            {
                                                                'name': 'docs',
                                                                'conclusion': 'NEUTRAL'
                                                            }
                                                        ]
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }

    @mock.patch('giscemultitools.githubutils.objects.GHAPIRequester')
    def test_get_pullrequest_checks_excludes_neutral_by_default(self, mock_requester_cls):
        mock_requester = mock_requester_cls.return_value
        mock_requester.get_pr_checks.return_value = self._build_checks_payload()

        checks = GithubUtils.get_pullrequest_checks('gisce', 'erp', 10)

        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]['name'], 'lint')

    @mock.patch('giscemultitools.githubutils.objects.GHAPIRequester')
    def test_get_pullrequest_checks_includes_neutral_when_requested(self, mock_requester_cls):
        mock_requester = mock_requester_cls.return_value
        mock_requester.get_pr_checks.return_value = self._build_checks_payload()

        checks = GithubUtils.get_pullrequest_checks('gisce', 'erp', 10, include_skyped=True)

        self.assertEqual(len(checks), 2)
        self.assertEqual({c['name'] for c in checks}, set(['lint', 'docs']))

    @mock.patch('giscemultitools.githubutils.utils.GithubUtils.get_pullrequest_checks')
    def test_get_pullrequest_check_status_returns_matching(self, mock_checks):
        mock_checks.return_value = [
            {'name': 'lint', 'conclusion': 'SUCCESS'}
        ]

        result = GithubUtils.get_pullrequest_check_status('gisce', 'erp', 10, 'lint')

        self.assertEqual(result, 'SUCCESS')

    @mock.patch('giscemultitools.githubutils.utils.GithubUtils.get_pullrequest_checks')
    def test_get_pullrequest_check_status_raises_when_missing(self, mock_checks):
        mock_checks.return_value = []

        with self.assertRaises(AssertionError):
            GithubUtils.get_pullrequest_check_status('gisce', 'erp', 10, 'lint')


class GithubUtilsChangelogTests(unittest.TestCase):
    @mock.patch('giscemultitools.githubutils.objects.GHAPIRequester')
    def test_project_changelog_groups_by_category_and_cleans_empty(self, mock_requester_cls):
        mock_requester = mock_requester_cls.return_value
        mock_requester.get_pulls_from_project.return_value = [
            {
                'title': 'Add invoicing report',
                'url': 'https://example/pr/30',
                'number': 30,
                'labels': ['comer', 'Eléctrico', 'ATR', 'deployed'],
                'status_change_date': '2023-03-10T12:00:00Z'
            },
            {
                'title': 'Unclassified PR',
                'url': 'https://example/pr/31',
                'number': 31,
                'labels': ['custom'],
                'status_change_date': '2023-03-11T12:00:00Z'
            }
        ]

        changelog = GithubUtils.project_changelog('gisce', 'erp', 'Proj')

        self.assertIn('comer', changelog)
        self.assertIn('Eléctrico', changelog['comer'])
        self.assertIn('ATR', changelog['comer']['Eléctrico'])
        pr_entry = changelog['comer']['Eléctrico']['ATR'][0]
        self.assertEqual(pr_entry['number'], 30)
        # ensure skip labels removed
        self.assertNotIn('deployed', pr_entry['labels'])

    @mock.patch('giscemultitools.githubutils.objects.GHAPIRequester')
    def test_project_changelog_filters_by_date(self, mock_requester_cls):
        mock_requester = mock_requester_cls.return_value
        mock_requester.get_pulls_from_project.return_value = [
            {
                'title': 'Old PR',
                'url': 'https://example/pr/20',
                'number': 20,
                'labels': ['comer', 'Eléctrico', 'ATR'],
                'status_change_date': '2022-12-31T23:59:00Z'
            }
        ]

        changelog = GithubUtils.project_changelog('gisce', 'erp', 'Proj', date_since='2023-01-01')

        self.assertEqual(changelog, {})

    def test_format_changelog_returns_markdown(self):
        changelog_data = {
            'comer': {
                'Eléctrico': {
                    'ATR': [
                        {
                            'title': 'Add report',
                            'number': 30,
                            'url': 'https://example/pr/30',
                            'labels': ['ATR']
                        }
                    ]
                }
            }
        }

        markdown = GithubUtils.format_changelog(changelog_data, project_name='Proj', format='markdown')

        self.assertIn('# Cambios Proj', markdown)
        self.assertIn('Add report [30](https://example/pr/30)', markdown)

class GithubUtilsChangelogV2Tests(unittest.TestCase):
    @mock.patch('giscemultitools.githubutils.objects.GHAPIRequester')
    def test_project_changelog_v2_groups_labels(self, mock_requester_cls):
        mock_requester = mock_requester_cls.return_value
        mock_requester.get_pulls_from_project.return_value = [
            {
                'title': 'Deploy virtual battery dashboards',
                'url': 'https://example/pr/101',
                'number': 101,
                'labels': [':fire: Top feature', 'Gas', 'analytics', 'migration'],
                'status_change_date': '2023-05-10T12:00:00Z',
                'mergedAt': '2023-05-09T12:00:00Z'
            },
            {
                'title': 'Improve monitoring alarms',
                'url': 'https://example/pr/102',
                'number': 102,
                'labels': ['monitoring', 'Stale'],
                'status_change_date': '2023-05-11T08:00:00Z',
                'mergedAt': '2023-05-10T12:00:00Z'
            },
            {
                'title': 'Docs tidy-up',
                'url': 'https://example/pr/103',
                'number': 103,
                'labels': ['doc', 'custom'],
                'status_change_date': '2023-05-11T09:00:00Z',
                'mergedAt': '2023-05-10T13:00:00Z'
            }
        ]

        changelog = GithubUtils.project_changelog_v2('gisce', 'erp', 'Growth Board')

        self.assertIn('Destacados', changelog['groups'])
        highlights = changelog['groups']['Destacados']['Funciones destacadas'][0]
        self.assertEqual(highlights['number'], 101)
        self.assertNotIn('migration', highlights['labels'])
        self.assertIn(':fire: Top feature', highlights['matched_labels'])

        ops_group = changelog['groups']['Operaciones y fiabilidad']['Monitorizacion y observabilidad'][0]
        self.assertEqual(ops_group['number'], 102)
        self.assertNotIn('Stale', ops_group['labels'])

        self.assertEqual(len(changelog['uncategorized']), 1)
        self.assertEqual(changelog['uncategorized'][0]['number'], 103)

    @mock.patch('giscemultitools.githubutils.objects.GHAPIRequester')
    def test_project_changelog_v2_respects_date_filter(self, mock_requester_cls):
        mock_requester = mock_requester_cls.return_value
        mock_requester.get_pulls_from_project.return_value = [
            {
                'title': 'Older monitoring fix',
                'url': 'https://example/pr/90',
                'number': 90,
                'labels': ['monitoring'],
                'status_change_date': '2023-02-01T12:00:00Z',
                'mergedAt': '2023-02-01T11:00:00Z'
            },
            {
                'title': 'Latest monitoring fix',
                'url': 'https://example/pr/91',
                'number': 91,
                'labels': ['monitoring'],
                'status_change_date': '2023-05-11T12:00:00Z',
                'mergedAt': '2023-05-11T11:00:00Z'
            }
        ]

        changelog = GithubUtils.project_changelog_v2('gisce', 'erp', 'Growth Board', date_since='2023-05-01')

        groups = changelog['groups']['Operaciones y fiabilidad']['Monitorizacion y observabilidad']
        numbers = [item['number'] for item in groups]
        self.assertEqual(numbers, [91])

    def test_format_changelog_v2_outputs_markdown(self):
        changelog_data = {
            'groups': OrderedDict([
                ('Destacados', OrderedDict([
                    ('Funciones destacadas', [
                        {
                            'title': 'Deploy virtual battery dashboards',
                            'number': 101,
                            'url': 'https://example/pr/101',
                            'labels': [':fire: Top feature', 'Gas'],
                            'matched_labels': [':fire: Top feature']
                        }
                    ])
                ]))
            ]),
            'uncategorized': [],
            'generated_at': '2023-05-12T12:00:00Z'
        }

        output = GithubUtils.format_changelog_v2(changelog_data, 'Growth Board')

        self.assertIn('# Cambios Growth Board (v2)', output)
        self.assertIn('Deploy virtual battery dashboards', output)
        self.assertIn('enfoque: :fire: Top feature', output)



if __name__ == '__main__':  # pragma: no cover
    unittest.main()
