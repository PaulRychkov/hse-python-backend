import json
from urllib.parse import parse_qs
from typing import Any, Awaitable, Callable

async def app(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None: 
    if scope['type'] != 'http':
        await send({
            'type': 'http.response.start',
            'status': 400,
            'headers': [(b'content-type', b'application/json')],
        })
        await send({
            'type': 'http.response.body',
            'body': json.dumps({"error": "Invalid scope type"}).encode(),
        })
        return
    
    method = scope.get('method')
    path = scope.get('path')
    
    if method is None or path is None:
        await send({
            'type': 'http.response.start',
            'status': 400,
            'headers': [(b'content-type', b'application/json')],
        })
        await send({
            'type': 'http.response.body',
            'body': json.dumps({"error": "Missing method or path in scope"}).encode(),
        })
        return

    status_code = 404
    response_body = json.dumps({"error": "Not Found"})

    if path == '/factorial' and method == 'GET':
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        n_values = query_params.get('n')
        status_code, response_body = await factorial(n_values)

    elif path.startswith('/fibonacci/') and method == 'GET':
        status_code, response_body = await fibonacci(path)

    elif path == '/mean' and method == 'GET':
        body = await receive_body(receive)
        status_code, response_body = await mean(body)

    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': [(b'content-type', b'application/json')],
    })

    await send({
        'type': 'http.response.body',
        'body': response_body.encode(),
    })

async def factorial(n_values: list):
    if not n_values or len(n_values) != 1:
        status_code = 422
        response_body = json.dumps({"error": "invalid n"})
    else:
        try:
            n = int(n_values[0])
            if n < 0:
                status_code = 400
                response_body = json.dumps({"error": "n must be a non-negative"})
            else:
                result = calculate_factorial(n)
                status_code = 200
                response_body = json.dumps({"result": result})
        except ValueError:
            status_code = 422
            response_body = json.dumps({"error": "n must be integer"})
    return status_code, response_body

async def fibonacci(path: str):
    try:
        n = int(path.split('/')[-1])
        if n < 0:
            status_code = 400
            response_body = json.dumps({"error": "n must be a non-negative integer"})
        else:
            result = calculate_fibonacci(n)
            status_code = 200
            response_body = json.dumps({"result": result})
    except ValueError:
        status_code = 422
        response_body = json.dumps({"error": "n must be integer"})
    return status_code, response_body

async def mean(body: bytes):
    try:
        numbers = json.loads(body)
        if not isinstance(numbers, list) or not all(isinstance(num, (int, float)) for num in numbers):
            status_code = 422
            response_body = json.dumps({"error": "elements must be valid floats"})
        elif not numbers:
            status_code = 400
            response_body = json.dumps({"error": "array cant be empty"})
        else:
            result = calculate_mean(numbers)
            status_code = 200
            response_body = json.dumps({"result": result})
    except json.JSONDecodeError:
        status_code = 422
        response_body = json.dumps({"error": "invalid format"})
    return status_code, response_body

async def receive_body(receive):
    body = b''
    more_body = True
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body

def calculate_factorial(n: int) -> int:
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def calculate_fibonacci(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def calculate_mean(numbers: list) -> float:
    return sum(numbers) / len(numbers)