# References
- https://learn.microsoft.com/en-us/azure/developer/python/sdk/azure-sdk-logging

# Too many logging.info messages

To avoid constant information messages like these:

    [2024-06-21T21:23:10.158Z] Response status: 201
    Response headers:
        'Content-Length': '0'
        'Content-MD5': 'REDACTED'
        'Last-Modified': 'Fri, 21 Jun 2024 21:23:14 GMT'
        'ETag': '"0x8DC92385C3422E3"'
        'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
        'x-ms-request-id': 'ff4473b6-901e-005c-5321-c4c23e000000'
        'x-ms-client-request-id': '75259de6-3014-11ef-afcf-a4b1c13ee715'
        'x-ms-version': 'REDACTED'
        'x-ms-content-crc64': 'REDACTED'
        'x-ms-request-server-encrypted': 'REDACTED'
        'Date': 'Fri, 21 Jun 2024 21:23:14 GMT'

Before running blob functions, change log level

```Python
import logging

# Set the logging level for all azure-* libraries                                    
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)
```