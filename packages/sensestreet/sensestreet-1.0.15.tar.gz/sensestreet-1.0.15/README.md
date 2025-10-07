# SenseStreetClient
This is a Python client for Sense Street API.

# Run the client
In order to use the client, import SenseStreetClient from sensestreet:
```
from sensestreet import SenseStreetClient
```
and provide the app_id and api_url:
```
client = SenseStreetClient(app_id="test", api_url="https://server.com/api")
```
To simply ping the server, use:
```
client.ping()
```

# Overview of all functions:

## Pings
```
ping()
```
Sends ping to the server to check if server is up and responding.

```
ping_auth()
```
Similar to ping but with authorisation - easy way to check if you're authorised to send requests to the server.

## Requests to prediction server:

```
predict_rfqs(conversation, options)
```
Sends request to predict rfqs in a conversation. Conversation has to be either a dict or a json.

```
chat_snippet_predict_rfqs(chat_snippet, options)
```
Sends request to predict rfqs in the conversation. Conversation has to be either a dict or a json. The difference between this function and the one above is the structure of the conversation, <em>predict_rfqs</em> is for a conversation in the Sense Street's format, while <em>chat_snippet_predict_rfqs</em> is for conversation that is a cutout from the chat.

## Batch job requests:
```
upload_files_with_conversations(files_paths)
```
Uploads specified files with conversation to be processed by the server. It returns an id for each file that will be nedded later on to obtain processed conversations. To run this function you need to have permission to open these files. Make sure you're not trying to upload over 1Gb of files in a single request.

```
upload_file_with_bond(file_path)
```
Uploads file with bond data to the server.

```
upload_erfq(file_path)
```
Uploads file with e-rfq data to the server.

```
get_processed_conv_file(file_id, save_path)
```
Returns file with processed conversations, <em>file_id</em> is the id that was returned during the files upload - by the <em>upload_files_with_conversations</em> function.

```
get_conv_file_status(file_id)
```
Returns the status of the uploaded file. With this function you can check if the file has already been processed by the server and is ready for download.

```
get_conv_file_history(since, until)
```
Retrieves the history of files uploded within the specified time range.  Returns a dictionary, where key is the file id, and value the timstamp of upload.
Example: 
```
from datetime import datetime
since = datetime(2024, 11, 1)
until = datetime.now()

print(client.get_conv_file_history(since, until))
```


# How to use your key to authorise requests
In order to send requests to the server you need to obtain a pair of keys - public and private (if you don't have a key contact the Sense Street to get one). In order to be correctly authorised by the server initialised the SenseStreetClient with the paths to both of the keys:

```
client = SenseStreetClient(
    app_id="id of your app",
    api_url="https://server.com/api",
    priv_key_path='path to your private key',
    pub_key_path='path to your public key'
    )
```

# How to define proxies
In order to use proxy provide a dict of proxies when initializing Sense Street Client, eg.:
```
client = SenseStreetClient(
    app_id="id of your app",
    api_url="https://server.com/api",
    request_args= { 'proxies': {
        "https": "https://10.10.1.10:1080",
            }
        }
    )
```

To read more about proxies refer to: https://requests.readthedocs.io/en/latest/user/advanced/#proxies
Similarly any additional request argument can be added:

```
client = SenseStreetClient(
    app_id="id of your app",
    api_url="https://server.com/api",
    request_args= { 'verify': 'path'
        }
    )
```

# anonymise_bbg_xml
anonymise_bbg_xml function takes input and output file paths and an optional pattern for identifying specific roles (bank vs client).

# example
Parameters:
xml_in: str - The input XML file path.
xml_out: str - The output file path where the anonymized XML will be saved.
bank_pattern: str - Regular expression pattern to identify bank side in conversation.

If bank_pattern is not provided, CompanyName and related fields are not anonymized.
```
from sensestreet import anonymise_bbg_xml

anonymise_bbg_xml(
    "./example.xml",  # Input XML file
    "./test.xml",     # Output XML file
)
```

### Fields Anonymized

| Field Name           | Example Replacement                  |
|-----------------------|---------------------------------------|
| `LoginName`          | Anonymized hash of the original name. |
| `FirstName`          | Randomized pseudonym.                 |
| `LastName`           | Randomized pseudonym.                 |
| `UUID`               | Blank  |
| `FirmNumber`         | Blank  |
| `AccountNumber`      | Blank  |
| `EmailAddress`       | Replaced with anonymized email based on `LoginName`. |
| `CorporateEmailAddress` | Replaced with anonymized email based on `LoginName`. |

# Anonymization Utilities

anonimize_to_hash(login: str, short: bool = True) -> str

Generates an anonymized hash representation of a login string.

Parameters:
login (str): The input string (e.g., username or email) to be anonymized.
short (bool, optional): Determines the encoding type for the hash.
True (default): Returns a Base85-encoded hash (shorter, more compact).
False: Returns a Base64-encoded hash.

Returns:
str: The anonymized hash as a string.

```
from sensestreet import anonimize_to_hash

login = "user@example.com"
short_hash = anonimize_to_hash(login, short=True)
print(short_hash)  # Outputs a Base85-encoded hash

long_hash = anonimize_to_hash(login, short=False)
print(long_hash)  # Outputs a Base64-encoded hash

```

anonimize_to_name(login: str) -> Tuple[str, str]

Generates a deterministic first and last name based on a login hash.

Parameters:
login (str): The input string (e.g., username or email) to be anonymized.
Returns:
Tuple[str, str]: A tuple containing the anonymized first name and last name.

```
from sensestreet import anonimize_to_name

login = "user@example.com"
first_name, last_name = anonimize_to_name(login)
print(f"Anonymized Name: {first_name} {last_name}")
```