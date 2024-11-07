import json

VCAP_SERVICES = {
    "VCAP_SERVICES": {
        "aws-elasticache-redis": [
            {
                "binding_guid": "5875b56b-042e-481c-a700-9640a5804d5b",
                "binding_name": None,
                "credentials": {
                    "current_redis_engine_version": "7.0",
                    "host": "master.prd-0aed712a-9055-4bde-a7a3-37f2fca117c3.pw1qnn.usgw1.cache.amazonaws.com",
                    "hostname": "master.prd-0aed712a-9055-4bde-a7a3-37f2fca117c3.pw1qnn.usgw1.cache.amazonaws.com",
                    "password": "uCZrIleHyUcUKxZlgsL1Q01H8",
                    "port": "6379",
                    "uri": "redis://:uCZrIleHyUcUKxZlgsL1Q01H8@master.prd-0aed712a-9055-4bde-a7a3-37f2fca117c3.pw1qnn.usgw1.cache.amazonaws.com:6379",
                },
                "instance_guid": "0aed712a-9055-4bde-a7a3-37f2fca117c3",
                "instance_name": "10x-ai-sandbox-redis",
                "label": "aws-elasticache-redis",
                "name": "10x-ai-sandbox-redis",
                "plan": "redis-3node-large",
                "provider": None,
                "syslog_drain_url": None,
                "tags": ["redis", "Elasticache", "AWS"],
                "volume_mounts": [],
            }
        ],
        "aws-rds": [
            {
                "binding_guid": "a8c76f70-f14d-4ac9-b474-7711d2970a4c",
                "binding_name": None,
                "credentials": {
                    "db_name": "cgawsbrokerprodqepps85ymuka5dq",
                    "host": "cg-aws-broker-prodqepps85ymuka5dq.ci7nkegdizyy.us-gov-west-1.rds.amazonaws.com",
                    "name": "cgawsbrokerprodqepps85ymuka5dq",
                    "password": "1yzztprpo0knsb2u0lik2tx1e",
                    "port": "5432",
                    "uri": "postgres://u7u83djsn0tfsl7c:1yzztprpo0knsb2u0lik2tx1e@cg-aws-broker-prodqepps85ymuka5dq.ci7nkegdizyy.us-gov-west-1.rds.amazonaws.com:5432/cgawsbrokerprodqepps85ymuka5dq",
                    "username": "u7u83djsn0tfsl7c",
                },
                "instance_guid": "755d13a0-c271-44a9-8aeb-a9ae686dcb5b",
                "instance_name": "gsa-ai-sandbox-small-psql-redundant",
                "label": "aws-rds",
                "name": "gsa-ai-sandbox-small-psql-redundant",
                "plan": "small-psql-redundant",
                "provider": None,
                "syslog_drain_url": None,
                "tags": ["database", "RDS"],
                "volume_mounts": [],
            },
            {
                "binding_guid": "6bd91767-d28f-497e-88c0-7cb8e6b477ba",
                "binding_name": None,
                "credentials": {
                    "db_name": "cgawsbrokerprodp5gy8iw0mkei4ud",
                    "host": "cg-aws-broker-prodp5gy8iw0mkei4ud.ci7nkegdizyy.us-gov-west-1.rds.amazonaws.com",
                    "name": "cgawsbrokerprodp5gy8iw0mkei4ud",
                    "password": "eqcmgp2ahjetqumbx0y1zb1f4",
                    "port": "5432",
                    "uri": "postgres://ubjsrm5sm8gqvlq4:eqcmgp2ahjetqumbx0y1zb1f4@cg-aws-broker-prodp5gy8iw0mkei4ud.ci7nkegdizyy.us-gov-west-1.rds.amazonaws.com:5432/cgawsbrokerprodp5gy8iw0mkei4ud",
                    "username": "ubjsrm5sm8gqvlq4",
                },
                "instance_guid": "8725fea1-0cd9-4cab-9804-e5c9c6c4360a",
                "instance_name": "gsa-ai-sandbox-large-psql-single-zone",
                "label": "aws-rds",
                "name": "gsa-ai-sandbox-large-psql-single-zone",
                "plan": "large-gp-psql",
                "provider": None,
                "syslog_drain_url": None,
                "tags": ["database", "RDS"],
                "volume_mounts": [],
            },
        ],
        "cloud-gov-identity-provider": [
            {
                "binding_guid": "ce442c5e-4eb5-4f02-a78d-04999ccb811c",
                "binding_name": None,
                "credentials": {
                    "client_id": "ce442c5e-4eb5-4f02-a78d-04999ccb811c",
                    "client_secret": ",rAQa9R3/6rKZexhcusXpZUvaSWPFzBV",
                },
                "instance_guid": "d8a832af-7dec-449e-b684-e1bdee1d4c87",
                "instance_name": "gsa-ai-sandbox-staging",
                "label": "cloud-gov-identity-provider",
                "name": "gsa-ai-sandbox-staging",
                "plan": "oauth-client",
                "provider": None,
                "syslog_drain_url": None,
                "tags": [],
                "volume_mounts": [],
            }
        ],
    }
}

VCAP_APPLICATION = {
    "VCAP_APPLICATION": {
        "application_id": "2773016f-5954-4a51-bea5-c0e6f8103539",
        "application_name": "gsa-ai-sandbox",
        "application_uris": ["gsa-ai-sandbox.app.cloud.gov"],
        "cf_api": "https://api.fr.cloud.gov",
        "limits": {"fds": 16384},
        "name": "gsa-ai-sandbox",
        "organization_id": "acc37c9f-9af0-4b35-a0ce-c7b043544971",
        "organization_name": "gsa-10x-prototyping",
        "space_id": "50924d21-1bc9-48a9-b772-746ed934d381",
        "space_name": "sandbox",
        "uris": ["gsa-ai-sandbox.app.cloud.gov"],
        "users": None,
    }
}

# Convert the dictionary to a single-line JSON string
json_string = json.dumps(VCAP_SERVICES, separators=(",", ":"))
print(json_string)
json_string = json.dumps(VCAP_APPLICATION, separators=(",", ":"))
print(json_string)
