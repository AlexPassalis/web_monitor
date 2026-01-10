---
name: writing-tests
description: Write tests following project conventions. Use when creating tests, adding test cases, or testing functions and endpoints.
---

# Writing Tests

## Instructions

1. Name tests `test_<function_name>` for functions, `test_<endpoint>_<method>` for endpoints
2. Use parameterized tests when a function has multiple code paths
3. Include at least one test case per code path
4. Keep tests focused on one behavior each
5. Follow code style: single quotes, fully typed, docstrings under function

## Examples

### Function test with parameterized cases

```python
@pytest.mark.parametrize('url,expected', [
    ('https://example.com', True),
    ('', False),
    ('not-a-url', False),
])
def test_validate_url(url: str, expected: bool) -> None:
    """Test URL validation with valid and invalid inputs."""
    result = validate_url(url)

    assert result == expected
```

### Endpoint test

```python
def test_webpage_get(client: Client) -> None:
    """Test fetching a webpage by ID."""
    webpage = Webpage.objects.create(url='https://example.com')

    response = client.get(f'/api/webpages/{webpage.id}')

    assert response.status_code == 200
    assert response.json()['url'] == 'https://example.com'
```

### Endpoint test for error case

```python
def test_webpage_get_not_found(client: Client) -> None:
    """Test 404 response for non-existent webpage."""
    response = client.get('/api/webpages/999')

    assert response.status_code == 404
```
