{"timestamp": "2025-09-26T17:03:38.401825", "level": "WARNING", "logger": "pyadvincekit.core.excel_parser",
 "message": "{\"event\": \"Unknown column type: Error Status\","
            " \"logger\": \"pyadvincekit.core.excel_parser\", "
            "\"timestamp\": \"2025-09-26T09:03:38.401824Z\", "
            "\"level\": \"warning\"}",
 "module": "excel_parser", "funcName": "_parse_column", "lineno": 215, "request_id": "unknown"}

{"timestamp": "2025-09-28T16:41:15.446217", "level": "INFO", "logger": "pyadvincekit.core.middleware",
 "message": "{\"extra\": {\"request_id\": \"7fc91268-8d3d-41b8-91f9-29e064d4d10c\", "
            "\"method\": \"POST\","
            " \"url\": \"http://localhost:8000/api/acct-book/auto/create\","
            " \"path\": \"/api/acct-book/auto/create\", "
            "\"query_params\": {}, \"headers\": {\"host\": \"localhost:8000\", \"connection\": \"keep-alive\", \"content-length\": \"785\", \"sec-ch-ua-platform\": \"\\\"Windows\\\"\", \"user-agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0\", \"accept\": \"application/json\", \"sec-ch-ua\": \"\\\"Chromium\\\";v=\\\"140\\\", \\\"Not=A?Brand\\\";v=\\\"24\\\", \\\"Microsoft Edge\\\";v=\\\"140\\\"\", \"content-type\": \"application/json\", \"sec-ch-ua-mobile\": \"?0\", \"origin\": \"http://localhost:8000\", \"sec-fetch-site\": \"same-origin\", \"sec-fetch-mode\": \"cors\", \"sec-fetch-dest\": \"empty\", \"referer\": \"http://localhost:8000/docs\", \"accept-encoding\": \"gzip, deflate, br, zstd\", \"accept-language\": \"zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\"}, \"client_ip\": \"127.0.0.1\"}, \"event\": \"\\u8bf7\\u6c42\\u5f00\\u59cb: POST /api/acct-book/auto/create\", \"logger\": \"pyadvincekit.core.middleware\", \"timestamp\": \"2025-09-28T08:41:15.445216Z\", \"level\": \"info\"}",
 "module": "middleware", "funcName": "dispatch", "lineno": 89, "request_id": "unknown"}





{"timestamp": "2025-09-28T16:41:15.446615", "level": "DEBUG", "logger": "pyadvincekit.core.database",
 "message": "{\"event\": \"\\u6570\\u636e\\u5e93\\u8fde\\u63a5\\u5df2\\u68c0\\u51fa\","
            " \"logger\": \"pyadvincekit.core.database\", "
            "\"timestamp\": \"2025-09-28T08:41:15.446615Z\", "
            "\"level\": \"debug\"}",
 "module": "database", "funcName": "checkout_event", "lineno": 103, "request_id": "unknown"}

{"timestamp": "2025-09-28T16:41:15.466420", "level": "DEBUG", "logger": "pyadvincekit.core.database",
 "message": "{\"event\": \"\\u6570\\u636e\\u5e93\\u8fde\\u63a5\\u5df2\\u5f52\\u8fd8\", \"logger\": \"pyadvincekit.core.database\", \"timestamp\": \"2025-09-28T08:41:15.466420Z\", \"level\": \"debug\"}",
 "module": "database", "funcName": "checkin_event", "lineno": 108, "request_id": "unknown"}

{"timestamp": "2025-09-28T16:41:15.466420", "level": "DEBUG", "logger": "pyadvincekit.core.database",
 "message": "{\"event\": \"\\u6570\\u636e\\u5e93\\u8fde\\u63a5\\u5df2\\u68c0\\u51fa\", \"logger\": \"pyadvincekit.core.database\", \"timestamp\": \"2025-09-28T08:41:15.466420Z\", \"level\": \"debug\"}",
 "module": "database", "funcName": "checkout_event", "lineno": 103, "request_id": "unknown"}

{"timestamp": "2025-09-28T16:41:15.475782", "level": "INFO", "logger": "pyadvincekit.crud.base",
 "message": "{\"event\": \"Created TMntxAcctBook with id 24033138-1d72-4433-9578-7e144a206521\", \"logger\": \"pyadvincekit.crud.base\", \"timestamp\": \"2025-09-28T08:41:15.475782Z\", \"level\": \"info\"}",
 "module": "base", "funcName": "create", "lineno": 231, "request_id": "unknown"}

{"timestamp": "2025-09-28T16:41:15.477303", "level": "DEBUG", "logger": "pyadvincekit.core.database",
 "message": "{\"event\": \"\\u6570\\u636e\\u5e93\\u8fde\\u63a5\\u5df2\\u5f52\\u8fd8\", \"logger\": \"pyadvincekit.core.database\", \"timestamp\": \"2025-09-28T08:41:15.477303Z\", \"level\": \"debug\"}",
 "module": "database", "funcName": "checkin_event", "lineno": 108, "request_id": "unknown"}

{"timestamp": "2025-09-28T16:41:15.478192", "level": "INFO", "logger": "pyadvincekit.core.middleware",
 "message": "{\"extra\": {\"request_id\": \"7fc91268-8d3d-41b8-91f9-29e064d4d10c\", \"status_code\": 201, \"duration\": 0.03297567367553711, \"response_headers\": {\"content-length\": \"980\", \"content-type\": \"application/json\", \"access-control-allow-origin\": \"*\", \"access-control-allow-credentials\": \"true\", \"x-content-type-options\": \"nosniff\", \"x-frame-options\": \"DENY\", \"x-xss-protection\": \"1; mode=block\", \"strict-transport-security\": \"max-age=31536000; includeSubDomains\", \"referrer-policy\": \"strict-origin-when-cross-origin\", \"x-process-time\": \"0.031577110290527344\"}}, \"event\": \"\\u8bf7\\u6c42\\u5b8c\\u6210: POST /api/acct-book/auto/create - 201 (0.033s)\", \"logger\": \"pyadvincekit.core.middleware\", \"timestamp\": \"2025-09-28T08:41:15.478192Z\", \"level\": \"info\"}",
 "module": "middleware", "funcName": "dispatch", "lineno": 134, "request_id": "unknown"}
