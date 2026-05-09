from app.services.search.providers import extract_search_rows


def test_extract_search_rows_supports_bocha_web_pages_shape():
    payload = {
        "code": 200,
        "data": {
            "webPages": {
                "value": [
                    {
                        "name": "利通电子公告",
                        "url": "https://www.cninfo.com.cn/example",
                        "snippet": "公告摘要",
                    }
                ]
            }
        },
    }

    rows = extract_search_rows(payload)

    assert rows == payload["data"]["webPages"]["value"]


def test_extract_search_rows_skips_non_dict_items():
    payload = {
        "data": {
            "webPages": {
                "value": [
                    "unexpected",
                    {
                        "title": "新闻",
                        "url": "https://example.com/news",
                    },
                ]
            }
        }
    }

    rows = extract_search_rows(payload)

    assert rows == [{"title": "新闻", "url": "https://example.com/news"}]
