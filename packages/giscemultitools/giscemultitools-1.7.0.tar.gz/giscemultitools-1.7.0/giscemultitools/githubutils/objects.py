# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import requests
import os
from json import loads, dumps


class RepositorySetUp(object):
    def __init__(self, owner, repository):
        self.owner = owner
        self.repository = repository


class GHAPIRequester(RepositorySetUp):
    def __init__(self, owner, repository):
        super(GHAPIRequester, self).__init__(owner, repository)
        if not os.environ.get('GITHUB_TOKEN'):
            raise EnvironmentError('Missing GITHUB_TOKEN environment variable')
        self.headers = {'Authorization': 'token {}'.format(os.environ.get('GITHUB_TOKEN'))}
        self.base_url = 'https://api.github.com/repos/{}/{}/'.format(self.owner, self.repository)
        self.graphql_url = 'https://api.github.com/graphql'

    def _request(self, url):
        r = requests.get(url, headers=self.headers)
        return loads(r.text)

    def _graphql_request(self, data):
        r = requests.post(self.graphql_url, data=data, headers=self.headers)
        return loads(r.text)

    def get_pulls_from_sha(self, sha):
        return self._request("{}commits/{}/pulls".format(self.base_url, sha))

    def get_commits_from_pr(self, pr):
        return self._request("{}pulls/{}/commits?per_page=100".format(self.base_url, pr))

    def get_project_info_from_project_name(self, project_name, only_one=False):
        query = """
            query {
                repository(owner: "%s", name: "%s") {
                    projectsV2(query: "name: %s", first: 60){
                        nodes {
                            id
                            number
                            title
                        }
                    }
                }
            }
        """ % (self.owner, self.repository, project_name)
        try:
            res = self._graphql_request(dumps({'query': query}))
            if only_one:
                return res['data']['repository']['projectsV2']['nodes'][0]
            else:
                return res['data']['repository']['projectsV2']['nodes']
        except Exception:
            raise UserWarning("{project_name} Not found".format(project_name=project_name))

    def get_pulls_from_project(self, project_name, pr_states=('merged',), project_status=('Done',)):
        pr_states = ','.join(pr_states)
        project_info = self.get_project_info_from_project_name(project_name, only_one=True)
        prs = []

        query = """
        {
          search(first: 100, query: "repo:%s/%s is:pr is:%s project:%s/%s", type: ISSUE) {
            edges {
              node {
                ... on PullRequest {
                  title
                  url
                  mergedAt
                  number
                  labels(first: 20){
                    nodes {
                      name
                    }
                  }
                  projectItems(first: 10) {
                    nodes {
                        project { id title number url }
                        id
                        type
                        fieldValues(last: 10) {
                            nodes {
                                ... on ProjectV2ItemFieldSingleSelectValue {
                                    id
                                    name
                                    updatedAt
                                    field {
                                      ... on ProjectV2SingleSelectField {
                                        id
                                        name
                                        options {
                                            name
                                            id
                                          }
                                      }
                                    }
                                }
                            }
                        }
                    }
                  }
                }
              }
            }
            pageInfo {
              endCursor
              hasNextPage
            }
          }
        }
        """ % (self.owner, self.repository, pr_states, self.owner, project_info['number'])
        first_result = self._graphql_request(dumps({'query': query}))
        cursor = first_result['data']['search']['pageInfo']['endCursor']
        has_next = first_result['data']['search']['pageInfo']['hasNextPage']
        for pr in first_result['data']['search']['edges']:
            status = [
                (_field['name'], _field['updatedAt']) for _field in
                [
                    _project_item
                    for _project_item in pr['node'].pop('projectItems')['nodes']
                    if _project_item['project']['title'] == project_name
                ][0]['fieldValues']['nodes']
                if _field.get('field', {}).get('name') == 'Status'
            ][0]
            if status[0] in project_status:
                pr['node']['labels'] = [_label['name'] for _label in pr['node']['labels']['nodes']]
                pr['node']['status_change_date'] = status[1]
                prs.append(pr['node'])

        next_query = """
        {
          search(first: 100, after: "%s", query: "repo:%s/%s is:pr is:%s project:%s/%s", type: ISSUE) {
            edges {
              node {
                ... on PullRequest {
                  title
                  url
                  mergedAt
                  number
                  labels(first: 20){
                    nodes {
                      name
                    }
                  }
                  projectItems(first: 10) {
                    nodes {
                        project { id title number url }
                        id
                        type
                        fieldValues(last: 10) {
                            nodes {
                                ... on ProjectV2ItemFieldSingleSelectValue {
                                    id
                                    name
                                    updatedAt
                                    field {
                                      ... on ProjectV2SingleSelectField {
                                        id
                                        name
                                        options {
                                            name
                                            id
                                          }
                                      }
                                    }
                                }
                            }
                        }
                    }
                  }
                }
              }
            }
            pageInfo {
              endCursor
              hasNextPage
            }
          }
        }
        """

        while has_next:
            next_result = self._graphql_request(
                dumps(
                    {
                        'query': next_query % (cursor, self.owner, self.repository, pr_states, self.owner, project_info['number'])
                    }
                )
            )
            cursor = next_result['data']['search']['pageInfo']['endCursor']
            has_next = next_result['data']['search']['pageInfo']['hasNextPage']

            for pr in next_result['data']['search']['edges']:
                status = [
                    (_field['name'], _field['updatedAt']) for _field in
                    [
                        _project_item
                        for _project_item in pr['node'].pop('projectItems')['nodes']
                        if _project_item['project']['title'] == project_name
                    ][0]['fieldValues']['nodes']
                    if _field.get('field', {}).get('name') == 'Status'
                ][0]
                if status[0] in project_status:
                    pr['node']['labels'] = [_label['name'] for _label in pr['node']['labels']['nodes']]
                    pr['node']['status_change_date'] = status[1]
                    prs.append(pr['node'])

        return prs

    def get_pull_request_projects_and_commits(self, pull_request_number):
        # mergeCommit.oid is the hash
        query = """
            query {
                repository(owner: "%s", name: "%s") {
                    pullRequest(number: %s) {
                        id
                        baseRefName
                        number
                        state
                        url
                        title
                        mergedAt
                        createdAt

                        milestone {
                          title
                        }

                        mergeCommit {
                            oid
                        }

                        commits(first: 250){
                            nodes {
                              commit {
                                oid
                              }
                            }
                        }
                        labels(first: 20){
                            nodes {
                              name
                            }
                        }

                        projectItems(first: 10) {
                            nodes {
                                project { id title number url }
                                id
                                type
                                fieldValues(last: 10) {
                                    nodes {
                                        ... on ProjectV2ItemFieldSingleSelectValue {
                                            id
                                            name
                                            field {
                                              ... on ProjectV2SingleSelectField {
                                                id
                                                name
                                                options {
                                                    name
                                                    id
                                                  }
                                              }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """ % (self.owner, self.repository, pull_request_number)
        return self._graphql_request(dumps({'query': query}))

    def update_projectv2_item_field_value(self, project_id, item_id, field_column_id, value):
        query = """
            mutation MyMutation {
              updateProjectV2ItemFieldValue(
                input: {projectId: "%s", itemId: "%s", fieldId: "%s", value: {singleSelectOptionId: "%s"}}
              ) {
                  clientMutationId
                  projectV2Item {
                    id
                  }
                }
            }

        """ % (project_id, item_id, field_column_id, value)
        return self._graphql_request(dumps({'query': query}))

    def add_item_to_project_v2(self, project_id, item_id):
        query = """
            mutation {
              addProjectV2ItemById(input: {projectId: "%s", contentId: "%s"}) {
                item {
                  id
                }
              }
            }
        """ % (project_id, item_id)
        return self._graphql_request(dumps({'query': query}))

    def get_pr_checks(self, pull_request_number):
        query = """
            query {
              repository(owner: "%s", name: "%s") {
                pullRequest(number: %s) {
                  commits(last: 1) {
                    nodes {
                      commit {

                        checkSuites(first: 100) {
                          nodes {
                            checkRuns(first: 100) {
                              nodes {
                                name
                                conclusion
                                permalink
                              }
                            }
                          }
                        }

                        status {
                          state
                          contexts {
                            state
                            targetUrl
                            description
                            context
                          }
                        }

                      }
                    }
                  }
                }
              }
            }
        """ % (
            self.owner, self.repository, pull_request_number
        )
        return self._graphql_request(dumps({'query': query}))
