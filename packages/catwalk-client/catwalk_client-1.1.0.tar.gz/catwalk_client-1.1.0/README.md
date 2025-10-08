# Catwalk Client

Catwalk is case aggregator for ML solutions where model query/responses can be collected for the later evaluation.  
This is client library helping to perform some common operations on the Catwalk API using python code.

## Install

Run `pip install catwalk-client`

## Sending cases

To send new open cases to the Catwalk instance you can use snippet below.

User can allow concurrent case collection while creating `CatwalkClient` by setting `concurrent` argument to `True`. The `ThreadPoolExecutor` is created with number of maximum workers passed by `max_workers` argument, by default it's 4 workers.

```python
    from catwalk_client import CatwalkClient

    # catwalk_url can be passed explicitly or can be provided in CATWALK_URL environment variable
    client = CatwalkClient(submitter_name="fatman", submitter_version="1.0.0", catwalk_url="http://localhost:9100", concurrent=True, max_workers=2)

    # direct call with dict to create new case
    client.send({
        "metadata": {"someint": 20},
        "query": [
            {"name": "lokalid", "value": "7386259234132", "type": "string"},
            {"name": "test3", "value": "yup", "type": "string"},
            {"name": "test2", "value": "yup", "type": "string"},
            {"name": "test1", "value": "yup", "type": "string"}
        ],
        "context": [],
        "response": [
            {
                "name": "predictions",
                "type": {
                    "name": "prediction",
                    "thresholds": [
                        {"from": 0, "to": 0.02, "label": "NO"},
                        {"from": 0.02, "to": 0.6, "label": "PERHAPS"},
                        {"from": 0.6, "to": 1, "label": "YES"}
                    ]
                },
                "value": {
                    "477110": 0.1493704617023468,
                    "477111": 0.3493704617023468,
                    "477112": 0.6493704617023468
                },
            }
        ]
    })

    # fluent API to create new cases
    client.new_case().add_query(
        name="some query key", value="1345243", type="str"
    ).add_query(
        name="other query key", value="1345243", type="str"
    ).add_context(
        name="photo", value="url", type="image"
    ).add_response(
        name="is_valid", value=True, type="bool"
    ).set_metadata(
        caller="esc-1"
    ).send()

```

### Result

When a case is successfully collected client should return ID of a collected case.

In some cases host might response with an error. In this case client will inform user that it ocurred
and it will display response status, error type and error message.

## Exporting cases

### Exporting case can be done programmatically, by including CatwalkClient in your code. It requires to input _AUTHORIZATION TOKEN_, you can find it by going to your `User profile`. Each environment (prod, preprod, dev, test) has different tokens.

To export cases from the Catwalk instance there is `export_cases` generator function available.

```python

    # catwalk_url can be passed explicitly or can be provided in CATWALK_URL environment variable
    # auth_token can be passed explicitly or can be provided in CATWALK_AUTH_TOKEN environment variable
    client = CatwalkClient(
        catwalk_url="https://catwalk.ikp-test-c3.kubernilla.dk/api", auth_token="*TOKEN*", insecure=False
    )


    def get_cw_data(client: CatwalkClient, name, version):
        data = []

        for case in client.export_cases(
            from_datetime=datetime(2023, 2, 8),
            to_datetime=datetime(2023, 2, 9),
            submitter_name=name,  # submitter_name is an optional argument,
            submitter_version=version,  # submitter_version is an optional argument,
            max_retries=5,
        ):
            print(case.id)
            data.append(case)

        print("Number of exported cases:", len(data))

        return data


    data = get_cw_data(client, "test", "0.0.1")

```

## Fetching a single case using `track_id`

```python
    case = client.get_case("test_track_id")
    print(case.dict())
```

## Fetching case evaluation results using `track_id`

```python
    case_evaluation_results = client.get_case_evaluation_results("test_track_id")
    print([e.dict() for e in case_evaluation_results])
```

## Updating a case

Replaces already existing case details with given data.

```python
    case_details = {
        "metadata": {"someint": 20},
        "query": [
            {"name": "lokalid", "value": "1234", "type": "number"},
        ],
        "context": [],
        "response": [
            {
                "name": "response",
                "type": "bool",
                "value": True,
            }
        ],
    }

    client.update("test_track_id", case_details)
```

## Altering a case

A way of updating a case. It first fetches the case by `track_id` as a `CaseBuilder` object.
This way it's easy to update `query`, `context`, `response`, or `metadata` of the case by
using the built-in methods.

### Notice:

**`set_metadata` method replaces the whole `metadata` property with a given value.**

```python
    case = client.alter_case("test_track_id")
    case.add_query("lokalid", "1234", "number")
    case.update()
```

## Initiating a session

A way of creating a session with cases assigned by track IDs. There are two ways to initiate a session.

### Method 1

```python
    session_id = client.create_session(
        session_name,
        session_description,
    )
    client.add_cases_to_session(session_id, track_ids)
    client.start_session(session_id, assign_to=["admin@example.com"])
```

### Method 2

```python
    client.initiate_session(
        session_name,
        track_ids,
        assign_to=["admin@example.com"],
        description=session_description,
    )
```

## Exceptions

Catwalk Client might end up throwing an exception. Here are a few that user can experience:

- **Connection error**: when the connection between client and host couldn't be established.
  This might occur either when user enters a wrong host address or when the host is offline.
- **ValidationError** or **TypeError**: when user enters wrongly formatted case.
- **Authorization Error (403)**: when user doesn't enter the authorization token (or enters one without appropriate permissions).
- **Other** - when any other error unhandled directly by Catwalk Client occurs it will
  display an exception name.
