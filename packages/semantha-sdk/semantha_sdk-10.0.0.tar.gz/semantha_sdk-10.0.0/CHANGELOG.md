# Changelog for the Python SDK for the semantha platform

## [10.0.0] 2025-10-09
### Removed
- **Matrix endpoints** - Removed matrix endpoints from platform server
- **has_opposite_meaning field** - Removed from Reference model and examples
- **do_contradiction_detection field** - Removed from DocumentTypeChange and DocumentTypeConfig models

### Added
- **New error codes** - Added JPEG2000_NOT_SUPPORTED and TRANSLATION_ERROR to ErrorFieldCodeEnum
- **Enhanced tag filtering** - Updated answers endpoint to support negation with "!" for tag groups

### Changed
- **Role requirements** - Updated document type endpoints to include 'Advanced User' role alongside existing 'Domain Admin' and 'Expert User' roles

## [9.0.0] 2025-06-17
### Added
- New endpoint to initiate a chat with a GenAI service: **/domains/{domainname}/chats/{id}** (POST)

## [8.12.0] 2025-05-14
### Added
- New endpoint to get and change domain-specific text types: **/domains/{domainname}/texttypes** (GET/PATCH)

## [8.10.0] 2025-04-23
### Added
- New parameter: _icon_name_ for prompts endpoint.
- New parameter _withreferenceimage_ for: **/bulk/domains/{domainname}/references**
- New endpoint to convert a Microsoft document (docx, pptx, xlsx) to PDF: **/conversions** (POST)

### Removed
- Parameter: _similarity_calculator_ has been removed from **/domains/{domainname}/settings**

## [8.9.0] 2025-04-02
### Added
- New endpoint to retrieve images of a document in library: **/domains/{domainname}/referencedocuments/{documentid}/images/{imageid}**
- New query parameter _addsourcedocument_ for: **/domains/{domainname}/referencedocuments**
- New output parameter: _was_chunked_ for answers and summarizations endpoints.

## [8.8.1] 2025-03-19
### Fixed
- fixed a bug which prevented dependencies from being correctly resolved (in version 8.8.0 only)

## [8.8.0] 2025-03-12
### Changed
- Error response is now specified: error_container.py, error_field.py, error_field_code_enum.py

### Added
- New parameter _addsourcedocument_ for: **/domains/{domainname}/referencedocuments**
- New parameter _withreferenceimage_ for: **/domains/{domainname}/references**

### Removed
- Parameters s and u have been removed from **/domains/{domainname}/summarizations**

## [8.6.0] 2025-02-04
### Changed
- Removed dependency to numpy

### Added
- Added top_k parameter to execution of prompts.

## [8.5.1] 2025-01-22
### Changed
- Return type of POST **/domains/{domainname}/prompts/{id}** is json object now

## [8.5.0] 2025-01-22
### Changed
- dropped support for Python 3.8 and 3.9

### Removed
- removed library_as_dataframe function in use case SDK

### Added
- new entity: Prompt with 6 CRUD services and an execution endpoint.
- new service to return (parts) of pdf page as png image: **/domains/{domainname}/documents** with accept header: image/png
- new field in Document and Documentinformation: "attachments", information about embedded files within a document
- new field in Document and Documentinformation: "mime_type"

## [8.3.0] 2024-11-28
### Added
- new parameter **tags** for endpoint: **/domains/{domainname}/answers** which filters the library.
- new parameter **maxanswerreferences** for endpoint: **/domains/{domainname}/answers** limits the number of references sent to a GenAI service.

## [8.2.0] 2024-11-14
### Added
- new endpoint **/domains/{domainname}/documentclasses/{id}/referencedocuments/tags**.

## [8.1.0] 2024-10-30
### Added
- new field in Settings: "enable_paragraph_length_comparison".

## [8.0.0] 2024-10-16
### Added
- new field in CellType: "hidden".
- new field in DocumentTypeChange: "viewport" and "ignoredPages".

## [7.13.0] 2024-10-02
### Added
- support for enums as part of objects in request/response.
- new field in document_type
- new field in settings

## [7.11.0] 2024-09-09
### Added
- support for reqifz as output document format.

## [7.10.0] 2024-08-28
### Added
- New parameters for  **/api/domains/{domainname}/documents** endpoint: 'withformatinfo'. Enable return of aggregated formatting information of paragraphs. 

## [7.9.0] 2024-08-09
no changes

## [7.8.0] 2024-07-24
### Added
- New parameters for  **/api/domains/{domainname}/documents** endpoint: 'withcharacters' and 'withsentences'. Enable/disable character and sentence data in the response.

## [7.5.0] 2024-06-13
### Added
- New field in domain settings: max_number_of_rows.

## [7.3.0] 2024-05-17
### Added
- New field in domain settings.

## [7.1.1] 2024-04-26
### Fixed
- wrong POST of IOBase in body.

## [7.1.0] 2024-04-23
### Added
- Client for accessing "Administration Product" where you can create an export/import of the content of domain.

### Fixed
- Fixed a bug where list of strings as an input parameter was not serialized properly.

## [7.0.0] 2024-04-09
- no changes

## [6.11.1] 2024-03-27
### Improved
- Better handling of circular imports.

## [6.11.0] 2024-03-20
### Added
- SDK supports enum input parameter now.
- Added summarylength parameter to **/api/domains/{domainname}/summarizations** endpoint.

### Improved
- Error message for bad requests on value errors contain a detailed explanation of what went wrong now.

## [6.10.0] 2024-03-07
### Added
- Added temperature parameter to **/api/domains/{domainname}/summarizations** endpoint.

### Improved
- More method and parameter comments

## [6.9.0] 2024-02-23
### Added
Added implementation method "post_json" for "overloaded" services where we have content type multipart/form-data as well as application/json: 
 - **/bulk/domains/{domainname}/referencedocuments** **POST**
 - **/domains/{domainname}/modelinstances** **POST**
 - **/domains/{domainname}/referencedocuments** **POST**
 - **/domains/{domainname}/similaritymatrix/cluster** **POST**


## [6.8.0] 2024-02-09
### Removed
- Removed two setting values: similarity_matcher and similarity_threshold for endpoint: **/domains/{domainname}/settings** **GET**

### Improved
- More method and parameter comments
- Endpoint **/domains** **GET** returns DomainInfo object now instead of Domain

## [6.7.0] 2024-01-29
### Improved
- More class and method comments, improved styling

## [6.6.0] 2024-01-18
### Added
- Added transactions endpoint: **/domains/{domainname}/transactions** **GET**

### Removed
- Removed deprecated endpoint: **/domains/{domainname}/documentcomparisons**

## [6.5.0] 2023-12-21
### Improved

- Reuse session object of requests library to increase performance on multiple calls

## [6.4.0] 2023-12-07
### Removed
- **/model/domains/{domainname}/documentcomparisons** **POST** (Accept: xlsx)

## [6.3.0] 2023-11-21
### Fixed
- PATCH and PUT methods with a list of dataclasses wasn't working.

### Added
- Added language parameter to /answers and /summarizations endpoints.

## [6.2.1] 2023-11-13
### Fixed
- Dataclasses aren't frozen anymore.
- Improved permission denied message with url.

## [6.2.0] 2023-11-09
### Added
- server_url is read from credentials.properties file now -> semantha_sdk.login(key_file = "credentials.properties") parameter key_file is enough now.
- server_url is read from json config file if present.
- Checks to normalize server_url

## [6.1.0] 2023-10-25
This version should only be used with a semantha server version >= 6.1

### Changed
- /api/info is versioned now and SDK calls /api/v3/info internally. This is a breaking change
- login() function and SemanthaAPI class are generated now

## [6.0.1] 2023-10-17
### Added
- Support for OAuth 2.0 Client Credentials Flow for credentials created via Semantha Administration UI.

## [6.0.0] 2023-10-04
### Fixed
- GET of files with different mimetype than application/json (e.g. get_as_docx)

## [5.11.1] 2023-09-21
### Removed
- **/model/domains/{domainname}/extractortables** has been removed
- **/model/domains/{domainname}/extractortables/{id}** has been removed

### Fixed
- fixed serialization on post of bulk endpoints with list of objects

## [5.11.0]
### Changed
- **/api/domains/{domainname}/summarizations** returns an object now instead of string.
- renamed class Metadata to ModelMetadata

## [5.10.0]
Improved Use Case SDK

## [5.9.0]
### Removed
- **/api/domains/{domainname}/referencedocuments/{documentid}/paragraphs/{id}/links**

## [5.8.0]
### Added
- **/api/domains/{domainname}/documentclasses/{id}/documentclasses**
- **/api/domains/{domainname}/documentclasses/{id}/referencedocuments**
- **/api/domains/{domainname}/referencedocuments/{documentid}/paragraphs/{id}/links**
- **/api/model/domains/{domainname}/backups**

SDK covers now 193/197 services.

## [5.7.0]
Added new endpoints in:
- **/api/domains/{domainname}/documenttypes/*** 
- **/api/domains/{domainname}/documentclasses/{id}/customfields**
- **/api/model/domains/{domainname}/classes/***

SDK covers now 184/197 services.


## [5.6.0]
Added most endpoints in **/api/models/* **
SDK covers now 158/180 services.

## [5.5.0]
Removed language parameter on **/api/domains/{domainname}/references**
Fixed bug on serialization of **/api/domains/{domainname}/modelinstances** response.
Fixed return of binary responses of bulk services.

## [5.4.0]
Added **new** service: 
- **/api/domains/{domainname}/summarizations** which generations a summarization for a given list of texts and a given topic.

Added support for **existing** services: 
- /api/model/domains/{domainname}/boostwords/{id}
- /api/model/domains/{domainname}/namedentities
- /api/model/domains/{domainname}/namedentities/{id}
- /api/model/domains/{domainname}/stopwords
- /api/model/domains/{domainname}/stopwords/{id}
- /api/model/domains/{domainname}/synonyms/{id}

## [5.3.0]

Added new service: **/api/domains/{domainid}/answers** with retrieval augemented answer generation based on your library entries.
Added new parameter on /modelinstances

## [5.2.0]

The SDK is now automatically generated from our openapi.json specification. It covers 71/169 (=42%) of all available services. Many class names and package names have been changed.

## [4.5.0]
Major restructuring of the SDK.
All sub-resources are directly accessible (instead of invoking getters).
That also means that (except for a few) all functions are plain get/post/delete/put/patch.
For example, in Versions < 4.5.0 a domain resource was fetched using `semantha_sdk.domains.get_one("domain_name")`.
Starting with 4.5.0 it is `semantha_sdk.domains("domain_name")`.
That also means that get/post/put/patch functions return semantha model objects (and never resources), which makes usage more consistent.
