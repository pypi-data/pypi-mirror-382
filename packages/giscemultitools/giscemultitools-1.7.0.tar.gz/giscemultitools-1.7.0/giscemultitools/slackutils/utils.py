class SlackUtils:
    @staticmethod
    def notify(hooks, data):
        import requests
        if hooks:
            hooks = hooks.replace(' ', '').split(',')
            for hook in hooks:
                res = requests.post(hook, data=data, headers={'Content-type': 'application/json'})
                print(res)

    @staticmethod
    def generic_notify_data(title, icon, message, origin):
        from datetime import datetime
        from json import dumps
        data_block = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": '{} {}'.format(title, icon)
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*When:*\n{}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    },
                    {
                        "type": "mrkdwn",
                        "text": '*FROM:*\n{}'.format(origin or " ")
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message or " "
                }
            }
        ]
        return dumps({"blocks": data_block})
