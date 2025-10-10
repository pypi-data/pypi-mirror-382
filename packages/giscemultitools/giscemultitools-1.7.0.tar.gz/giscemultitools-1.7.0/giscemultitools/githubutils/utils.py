# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .changelog_v2 import ChangelogBuilderV2, format_changelog_v2 as _format_changelog_v2

class GithubUtils:
    @staticmethod
    def plain_get_commits_sha_from_merge_commit(response):
        res = {
            'commits': [
                commit['commit']['oid'] for commit in response['data']['repository']['pullRequest']['commits']['nodes']
            ],
            'pullRequest': {
                'id': response['data']['repository']['pullRequest']['id'],
                'number': response['data']['repository']['pullRequest']['number'],
                'state': response['data']['repository']['pullRequest']['state'],
                'milestone': response['data']['repository']['pullRequest']['milestone'] and response['data']['repository']['pullRequest']['milestone']['title'] or '',
                'url': response['data']['repository']['pullRequest']['url'],
                'title': response['data']['repository']['pullRequest']['title'],
                'baseRefName': response['data']['repository']['pullRequest']['baseRefName'],
                'mergedAt': response['data']['repository']['pullRequest']['mergedAt'],
                'createdAt': response['data']['repository']['pullRequest']['createdAt'],
                'labels': response['data']['repository']['pullRequest']['labels']['nodes']
            },
            'projectItems': []
        }
        for card in response['data']['repository']['pullRequest']['projectItems']['nodes']:
            pos_status = 0
            for i, node in enumerate(card['fieldValues']['nodes']):
                if node and node.get('field', {}).get('name') == 'Status':
                    pos_status = i
                    break

            res['projectItems'].append(
                {
                    'project_name': card['project']['title'],
                    'project_id': card['project']['id'],
                    'project_url': card['project']['url'],
                    'card_state': card['fieldValues']['nodes'][pos_status]['name'],
                    'field_id': card['fieldValues']['nodes'][pos_status]['id'],
                    'field_column_id': card['fieldValues']['nodes'][pos_status]['field']['id'],
                    'field_column_options': {
                        opt['name']: opt['id'] for opt in card['fieldValues']['nodes'][pos_status]['field']['options']
                    },
                    'card_id': card['id']
                }
            )

        return res

    @staticmethod
    def get_pr_from_sha_merge_commit(owner, repository, sha):
        from .objects import GHAPIRequester
        requester = GHAPIRequester(owner, repository)

        pulls = requester.get_pulls_from_sha(sha)
        if not isinstance(pulls, (tuple, list)):
            raise Exception(pulls)

        pull_request_number = None
        for pr in pulls:
            if pr['merge_commit_sha'] == sha:
                pull_request_number = pr['number']
                break
        if pull_request_number is None:
            raise AssertionError("PR Not Found, Did you specified a merge commit?")
        return pull_request_number

    @staticmethod
    def get_commits_sha_from_merge_commit(owner, repository, sha):
        from .objects import GHAPIRequester
        requester = GHAPIRequester(owner, repository)

        pulls = requester.get_pulls_from_sha(sha)
        if not isinstance(pulls, (tuple, list)):
            raise Exception(pulls)

        pull_request_number = None
        for pr in pulls:
            if pr['merge_commit_sha'] == sha:
                pull_request_number = pr['number']
                break

        if pull_request_number is None:
            raise AssertionError("PR Not Found, Did you specified a merge commit?")

        pr_info = requester.get_pull_request_projects_and_commits(pull_request_number=pull_request_number)
        pr_info = GithubUtils.plain_get_commits_sha_from_merge_commit(pr_info)

        return pr_info

    @staticmethod
    def get_pullrequest_info(owner, repository, pr_number):
        from .objects import GHAPIRequester
        requester = GHAPIRequester(owner, repository)

        pr_info = requester.get_pull_request_projects_and_commits(pull_request_number=pr_number)
        pr_info = GithubUtils.plain_get_commits_sha_from_merge_commit(pr_info)

        return pr_info

    @staticmethod
    def get_pullrequest_context_checks(owner, repository, pr_number):
        from .objects import GHAPIRequester
        requester = GHAPIRequester(owner, repository)
        pr_info = requester.get_pr_checks(pull_request_number=pr_number)
        res = []
        last_commit_info = pr_info['data']['repository']['pullRequest']['commits']['nodes'][0]['commit']
        if last_commit_info.get('status'):
            for _node in last_commit_info['status']['contexts']:
                if _node.get('context'):
                    res.append(_node)

        def _humanize(_res):
            return [{'name': _r['context'], 'conclusion': _r['state'], 'permalink': _r['targetUrl']} for _r in _res]

        return _humanize(res)

    @staticmethod
    def get_pullrequest_context_check_status(owner, repository, pr_number, check_name):
        context_checks = GithubUtils.get_pullrequest_context_checks(owner, repository, pr_number)
        for context_check in context_checks:
            if context_check['name'] == check_name:
                return context_check['conclusion']

        raise AssertionError('Check {} not found in PR {}'.format(check_name, pr_number))

    @staticmethod
    def get_pullrequest_checks(owner, repository, pr_number, include_skyped=False):
        from .objects import GHAPIRequester
        requester = GHAPIRequester(owner, repository)
        pr_info = requester.get_pr_checks(pull_request_number=pr_number)
        checks = []
        res = [
            _node['checkRuns'] for _node in
            pr_info['data']['repository']['pullRequest']['commits']['nodes'][0]['commit']['checkSuites']['nodes']
            if _node.get('checkRuns', {}).get('nodes')
        ]
        for _check_run in res:
            for _node in _check_run['nodes']:
                if _node['conclusion'] != 'NEUTRAL' or include_skyped:
                    checks.append(_node)

        return checks

    @staticmethod
    def get_pullrequest_check_status(owner, repository, pr_number, check_name, include_skyped=False):
        checks_info = GithubUtils.get_pullrequest_checks(owner, repository, pr_number, include_skyped)

        for _check in checks_info:
            if _check.get('name') == check_name:
                return _check['conclusion']

        raise AssertionError('Check {} not found in PR {} or is skyped'.format(check_name, pr_number))

    @staticmethod
    def update_projectv2_item_field_value(owner, repository, project_id, item_id, field_column_id, value):
        from .objects import GHAPIRequester
        requester = GHAPIRequester(owner, repository)
        return requester.update_projectv2_item_field_value(project_id, item_id, field_column_id, value)

    @staticmethod
    def add_item_to_project(owner, repository, project_id, item_id):
        from .objects import GHAPIRequester
        requester = GHAPIRequester(owner, repository)
        return requester.add_item_to_project_v2(project_id, item_id)

    @staticmethod
    def add_prs_to_project_by_name(owner, repository, project_name, prs_list):
        from giscemultitools.githubutils.objects import GHAPIRequester
        requester = GHAPIRequester(owner, repository)
        res = requester.get_project_info_from_project_name(project_name, only_one=True)
        project_id = res['id']
        for _pr in prs_list:
            human_pr = GithubUtils.plain_get_commits_sha_from_merge_commit(
                requester.get_pull_request_projects_and_commits(_pr)
            )
            pr_id = human_pr['pullRequest']['id']
            if project_id not in [x['project_id'] for x in human_pr['projectItems']]:
                res = GithubUtils.add_item_to_project(owner, repository, project_id, pr_id)
                print('Added {} to project {}'.format(_pr, project_name))
            else:
                print('{} already in project {}'.format(_pr, project_name))

    @staticmethod
    def get_pulls_from_project_and_column(owner, repository, project_name, card_status):
        from .objects import GHAPIRequester
        requester = GHAPIRequester(owner, repository)
        res = []
        for _pr_state in ('merged', 'open'):
            included_prs = requester.get_pulls_from_project(project_name, pr_states=(_pr_state,), project_status=(card_status,))
            res.extend(included_prs)
        return res

    @staticmethod
    def project_changelog_v2(owner, repository, project_name, date_since=None, label_groups=None, ignored_labels=None):
        from .objects import GHAPIRequester
        requester = GHAPIRequester(owner, repository)
        pulls = requester.get_pulls_from_project(project_name, pr_states=('merged',), project_status=('Done',))
        normalized_pulls = []
        for pull in pulls:
            normalized_pulls.append({
                'title': pull.get('title'),
                'number': pull.get('number'),
                'url': pull.get('url'),
                'labels': pull.get('labels', []),
                'status_change_date': pull.get('status_change_date'),
                'mergedAt': pull.get('mergedAt')
            })
        builder = ChangelogBuilderV2(label_groups=label_groups, ignored_labels=ignored_labels)
        return builder.build(normalized_pulls, date_since=date_since)

    @staticmethod
    def format_changelog_v2(changelog_data, project_name, output_format='markdown'):
        return _format_changelog_v2(changelog_data, project_name, output_format)

    @staticmethod
    def project_changelog(
            owner, repository, project_name,
            categories=('comer', 'distri'),
            sub_categories=('Eléctrico', 'Gas', 'oficinavirtual'),
            top_labels=('ATR', 'facturacio', 'core', 'GIS', 'medidas'),
            skip_labels=('custom',),
            skip_shown_labels=(
                '(local run) to be merged', 'to be merged', 'deployed', 'deployed PRE', 'Fix my tests pls',
                'Fix Tests'
            ),
            date_since=None
    ):
        from .objects import GHAPIRequester
        from datetime import datetime
        if date_since is not None:
            date_since = datetime.strptime(date_since, '%Y-%m-%d')
        requester = GHAPIRequester(owner, repository)
        included_prs = requester.get_pulls_from_project(project_name, pr_states=('merged',), project_status=('Done',))

        if not included_prs:
            return {}

        changelog_data = {
            _category: {
                _sub_category: {
                    _label: [] for _label in top_labels + ('Otras',)
                }
                for _sub_category in sub_categories + ('Otras',)
            } for _category in categories
        }
        not_classified_prs = []

        for _pr in included_prs:
            # Check for skip labels
            if (
                    not set.intersection(set(_pr['labels']), set(skip_labels))
                    and (
                        date_since is None
                        or datetime.strptime(_pr['status_change_date'], '%Y-%m-%dT%H:%M:%SZ') >= date_since
                    )
            ):
                _pr['labels'] = [_pr_label for _pr_label in _pr['labels'] if _pr_label not in skip_shown_labels]
                classified = False
                for _category in categories:
                    if _category in _pr['labels']:
                        classified = True
                        sub_classified = False
                        for _sub_category in sub_categories:
                            if _sub_category in _pr['labels']:
                                sub_classified = True
                                tag_classified = False
                                for _tag in top_labels:
                                    if _tag in _pr['labels']:
                                        tag_classified = True
                                        changelog_data[_category][_sub_category][_tag].append(_pr)
                                if not tag_classified:
                                    changelog_data[_category][_sub_category]['Otras'].append(_pr)
                        if not sub_classified:
                            changelog_data[_category]['Otras']['Otras'].append(_pr)
                if not classified:
                    not_classified_prs.append(_pr)

        # TODO show not classified

        # clean void sections
        for _k in list(changelog_data.keys()):
            for _sk in list(changelog_data[_k].keys()):
                for _skl in list(changelog_data[_k][_sk].keys()):
                    if not changelog_data[_k][_sk][_skl]:
                        del changelog_data[_k][_sk][_skl]
                if not changelog_data[_k][_sk]:
                    del changelog_data[_k][_sk]
            if not changelog_data[_k]:
                del changelog_data[_k]

        return changelog_data

    @staticmethod
    def format_changelog(changelog_data, project_name, format='html'):
        """
        @param changelog_data: s
        @param project_name:
        @param format: html, markdown
        @return:
        """
        from datetime import datetime
        changelog = ""
        if not changelog_data:
            return changelog

        if format == 'html':
            pass
        elif format == 'markdown':
            changelog = "# Cambios {project_name} {date_today}\n".format(
                project_name=project_name, date_today=datetime.today().strftime('%Y-%m-%d')
            )
            for _k in changelog_data.keys():
                changelog += "## {category}\n".format(category=_k)
                for _sk in changelog_data[_k].keys():
                    changelog += "- ### {sub_category}\n".format(sub_category=_sk)
                    for _skl in changelog_data[_k][_sk].keys():
                        changelog += "  - **{label}**\n".format(label=_skl)
                        for _pr in changelog_data[_k][_sk][_skl]:
                            changelog += "    - {title} [{pr_number}]({pr_url})\n\n".format(
                                title=_pr['title'], pr_number=_pr['number'], pr_url=_pr['url']
                            )
                            changelog += "      **{labels}**\n".format(labels=_pr['labels'])

        return changelog
