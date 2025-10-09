![](https://www.semantha.de/wp-content/uploads/semantha-inverted.svg)

# 💜 semantha SDK

The semantha SDK is a high-level REST client to access the [semantha](http://semantha.ai) API.
The SDK is updated in parallel to each new version of semantha (typically every 2 weeks). Use the same SDK version as your semantha server version.
An overview of the currently supported endpoints may be found at the end of this document (see section "State of Development").
The semantha SDK is compatible with python >= 3.10.

## 🔬 Design guideline/idea
Every api call can easily be translated into a python sdk call where the HTTP method becomes the last method:
* `GET /api/info -> api.info.get()`

Parameters in the URL become method parameters:
* `POST /api/domains/<your_domain>/referencedocuments -> api.domains("<your_domain>").referencedocuments.post(file=somefile)`

The SDK offers type hints and doc strings for services, parameters, input types and return types within your IDE.

## 📝 Changelog
See list of changes below.

## 🚀 Quickstart
1. If you have access to semantha you can create your own login credentials: As a domain administrator go to "Administration" App -> then select "Client Administration" in the upper dropdown. Here you can add a new "client" by clicking "+ Add new". Configure "Domain Access", "App Access" (not used so far) and Roles. Click "Add" and download the credentials.properties file via the action menu. You can use this properties file to login with the SDK. See an example below.
1. In case you are not a semantha user already you can request a demo access to semantha's API via [this contact form](https://www.semantha.de/request/).

### Authentication with client credentials.properties file

```python
import semantha_sdk
# file name has to end with '.properties'!
api = semantha_sdk.login(key_file="credentials.properties")
print("Talking to semantha server: " + api.info.get().version)
```

Alternatively you can set the 4 parameters: server_url, client_id, client_secret and token_url with the values from your credentials.properties files.

```python
import semantha_sdk
api = semantha_sdk.login(server_url="<semantha server URL>", client_id="<id>", client_secret="<secret>", token_url="<url>")
print("Talking to semantha server: " + api.info.get().version)
```

### Old: Authentication with API key

```python
import semantha_sdk
api = semantha_sdk.login(server_url="<semantha server URL>", key="<your key>")
print("Talking to semantha server: " + api.info.get().version)
```

### Old: Authentication with json key file

```python
import semantha_sdk
#file name has to end with '.json'!
api = semantha_sdk.login(server_url="<semantha server URL>", key_file="<path to your key file (json format)>")
# end-points (resp. resources) can be used like objects
my_domain = api.domains("my_domain")
# they may have sub-resources, which can be retrieved as objects as well
reference_documents = my_domain.referencedocuments
# GET all reference documents
print("Library contains "+ len(reference_documents.get()) + " entries")
```

Example key file in json format:

```json
{ "API_Key" : "<your key>",
  "server_url": "<your serverurl>" }
```

### CRUD on End-points

```python
# CRUD operations are functions
domain_settings = my_domain.settings.get()
#Warning: this deletes ALL reference documents/library entries
my_domain.referencedocuments.delete() 
```

### Function Return Types & semantha Data Model

```python
# some functions only return None, e.g.
my_domain.referencedocuments.delete() # returns NoneType

# others return built in types, e.g
roles_list = currentuser.roles.get() # returns List[str]

# but most return objects of the semantha Data Model
# (all returned objects are instances of frozen dataclasses)
settings = my_domain.settings.get() # returns instance of Settings
# attributes can be accessed as properties, e.g.
settings.enable_tagging # returns true or false
# Data Model objects may be complex
document = my_domain.references.post(file=a, referencedocument=b) # returns instance of Document
# the following returns the similarity value of the first references of the first sentence of the
# the first paragraph on the first page of the document (if a reference was found for this sentence)
similarity = pages[0].contents[0].paragraphs[0].references[0].similarity # returns float
```

### Getting an annotated pdf and saving it locally

```python
import semantha_sdk
api = semantha_sdk.login(server_url="<semantha server URL>", key="<your key>")
domain = "<your domain>"
pdf = open('<your_file>.pdf', 'rb')
annotated_pdf = api.domains(domain).documentannotations.post_as_pdf(file=pdf, similaritythreshold=0.85)
with open('annotated.pdf', 'wb') as annotated_file:
    annotated_file.write(annotated_pdf.getbuffer())
```
