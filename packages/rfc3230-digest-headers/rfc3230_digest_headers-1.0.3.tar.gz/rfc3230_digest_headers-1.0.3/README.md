[![Test](https://github.com/Mari6814/py-rfc3230-digest-headers/actions/workflows/ci.yml/badge.svg)](https://github.com/Mari6814/py-rfc3230-digest-headers/actions/workflows/ci.yml)
[![Coverage](https://github.com/Mari6814/py-rfc3230-digest-headers/raw/main/badges/coverage.svg)](https://github.com/Mari6814/py-rfc3230-digest-headers/raw/main/badges/coverage.svg)
[![Versions](https://github.com/Mari6814/py-rfc3230-digest-headers/raw/main/badges/python-versions.svg)](https://github.com/Mari6814/py-rfc3230-digest-headers/raw/main/badges/python-versions.svg)

# Introduction

A small library to provide the server and client side methods to require, negotiation and generate `Digest` HTTP headers as per [RFC 3230](https://datatracker.ietf.org/doc/html/rfc3230).
Clients can generate `Digest` headers of the form: `Digest: SHA-256=xyz, MD5=abc`. Server can require certain algorithms by sending `Want-Digest` headers of the form: `Want-Digest: SHA-256, SHA;q=0.5, MD5;q=0`.

# Installation

Install using pip:

```bash
pip install rfc3230-digest-headers
```

# Overview of the protocol

The protocol works as follows:

1. Client and server agree on what the `instance` bytes are for the endpoint in question. Usually the request body or the content of the resource before applying transformations.
2. Client sends request
3. If the client did not directly send a valid `Digest`, the server responds with `Want-Digest` header to indicate which algorithms it supports.
   - Form of the `Want-Digest` header: `Want-Digest: SHA-256, SHA;q=0.5, MD5;q=0`
   - The server can specify `qvalues` to indicate preference of algorithms.
   - No value equals `q=1.0`.
   - `q=0` means "do not use this algorithm".
4. Client generates `Digest` header using one of the supported algorithms and sends it in the request.
   - Form of the `Digest` header: `Digest: SHA-256=xyz, MD5=abc`
5. Server verifies the `Digest` header and processes the request.

# Usage

The library provides only one enum class, `DigestHeaderAlgorithm`, which can be used by server and client to fully specify, negotiate and generate `Digest` HTTP headers.
You do not use these algorithms directly, but instead have to use a couple of _static_ methods provided by the enum class.

## Example: Generate a `Digest` header

The client generates a `Digest` for their _instance_.

```python
from rfc3230_digest_headers import DigestHeaderAlgorithm

instance_bytes = b"Hello, World!"
header = DigestHeaderAlgorithm.make_digest_header(
    instance=instance_bytes,
    algorithms=[DigestHeaderAlgorithm.SHA256, DigestHeaderAlgorithm.MD5]
)
print(header.header_name)  # "Digest"
print(header.header_value) # "SHA-256=..., MD5=..."
```

## Usage: Verify a `Digest` header

The server receives a request with a `Digest` header and verifies it.

```python
from rfc3230_digest_headers import DigestHeaderAlgorithm

instance_bytes = b"Hello, World!"
request_headers = {"Digest": "SHA-256=..., MD5=..."}
is_valid, want_digest_header_should_be_added = DigestHeaderAlgorithm.verify_request(
    request_headers=request_headers,
    instance=instance_bytes,
    qvalues={
        DigestHeaderAlgorithm.SHA256: 1.0,
        DigestHeaderAlgorithm.SHA: 0.5,
        DigestHeaderAlgorithm.MD5: 0.0 # If the client sends MD5, they will receive an error
    },
)
print(is_valid)  # True if the Digest header is valid
print(want_digest_header_should_be_added)  # None if valid, otherwise contains the `Want-Digest` header to be sent to the client for negotiation
```

## Usage: Server-side negotiation of algorithms

The server can indicate which algorithms the endpoint requires by sending a `Want-Digest` header. The header is automatically generated when attempting to verify invalid request headers. In the following example, the client sends a `Digest` header with an unsupported algorithm (`MD5` with a _q-value_ of `0.0`), so the server responds with a `Want-Digest` header indicating which algorithms are supported.

```python
from rfc3230_digest_headers import DigestHeaderAlgorithm

# Fake request from client without an invalid Digest header
instance_bytes = b"Hello, World!"
request_headers = {"Digest": "SHA-256=..., MD5=..."}
is_valid, want_digest_header_should_be_added = DigestHeaderAlgorithm.verify_request(
    request_headers=request_headers,
    instance=instance_bytes,
    qvalues={
        DigestHeaderAlgorithm.SHA256: 1.0,
        DigestHeaderAlgorithm.SHA: 0.5,
        DigestHeaderAlgorithm.MD5: 0.0 # If the client sends MD5, they will receive an error
    },
)
if want_digest_header_should_be_added:
    print(want_digest_header_should_be_added.header_name)  # "Want-Digest"
    print(want_digest_header_should_be_added.header_value) # "SHA-256, SHA;q=0.5, MD5;q=0"
    # Send the response with the generated Want-Digest header
    ...
```

## Usage: Client-side negotiation of algorithms

When an endpoint responds with a `Want-Digest` header, the client can parse it and generate a valid `Digest` header. In the following example, imagine that we initially sent a request with `b'Hello, World!'` as body, and the server responded with an HTTP error code and a `Want-Digest` header. The client sees that its original request failed, and that the server wants a `Digest` header. The client then generates a valid `Digest` header using the highest priority algorithm from the `Want-Digest` header and re-sends the request.

```python
from rfc3230_digest_headers import DigestHeaderAlgorithm

# Fake response from server with Want-Digest header
instance_bytes = b"Hello, World!"
want_digest_header_value = "SHA-256, SHA;q=0.5, MD5;q=0"

# Parse the response and generate a valid Digest header (if possible)
header = DigestHeaderAlgorithm.handle_want_digest_header(
    instance=instance_bytes,
    want_digest_header=want_digest_header_value,
    algorithms="auto"  # Use the highest priority algorithm from Want-Digest
)
print(header.header_name)   # "Digest"
print(header.header_value)  # "sha-256=..."

# re-send the request with the generated Digest header
...
```
