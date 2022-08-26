import random

from britive.britive import Britive
import random


b = Britive()  # source tenant and token from env vars

# name of the service identity (and associated policy)
# change as required
name = 'audit-logs-to-s3-reader8'

policy = {
    "name": name,
    "description": "",
    "isActive": True,
    "isDraft": False,
    "members": {
        "serviceIdentities": [
            {
                "name": name
            }
        ]
    },
    "roles": [
        {
            "name": "AuditLogViewRole"
        }
    ],
    "accessType": "Allow"
}


def process():
    service_identity = b.service_identities.create(
        name=name
    )
    print(f'created service identity: {service_identity["userId"]}:{name}')
    token = b.service_identity_tokens.create(
        service_identity_id=service_identity['userId']
    )
    print(f'created token: {token["token"]}')

    # no SDK action for this yet so just hard coding it for now
    b.post(
        url=f'https://{b.tenant}.britive-app.com/api/v1/policy-admin/policies',
        json=policy
    )

    print(f'created policy which added {name} to allow use of role AuditLogViewRole')


if __name__ == '__main__':
    process()
