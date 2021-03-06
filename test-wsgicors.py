from webob import Request, Response
from wsgicors import make_middleware as mw
from nose import with_setup

deny = {"policy":"deny"}

free = {"policy":"pol", 
        "pol_origin":"*", 
        "pol_methods":"*", 
        "pol_headers":"*",
        "pol_credentials":"true",
        "pol_maxage":"100"
        }

free_nocred = {"policy":"pol", 
        "pol_origin":"*", 
        "pol_methods":"*", 
        "pol_headers":"*",
        "pol_credentials":"false",
        "pol_maxage":"100"
        }

verbatim = {"policy":"pol", 
        "pol_origin":"example.com", 
        "pol_methods":"put,delete", 
        "pol_headers":"header1,header2",
        "pol_credentials":"true",
        "pol_maxage":"100"
        }

post2 = post = preflight = None

def setup():
    global preflight, post, post2

    preflight = Request.blank("/")
    preflight.method="OPTIONS"
    preflight.headers["Access-Control-Request-Method"] = "post"
    preflight.headers["Access-Control-Request-Headers"] = "*"

    post = Request.blank("/")
    post.method="POST"
    post.headers["Origin"] = "example.com"

    post2 = Request.blank("/")
    post2.method="POST"
    post2.headers["Origin"] = "example2.com"

@with_setup(setup)
def testdeny():
    corsed = mw(Response(), deny)
    res = preflight.get_response(corsed)
    assert "Access-Control-Allow-Origin" not in res.headers
    assert "Access-Control-Allow-Credentials" not in res.headers
    assert "Access-Control-Allow-Methods" not in res.headers
    assert "Access-Control-Allow-Headers" not in res.headers
    assert "Access-Control-Max-Age" not in res.headers

    res = post.get_response(corsed)
    assert "Access-Control-Allow-Origin" not in res.headers
    assert "Access-Control-Allow-Credentials" not in res.headers

@with_setup(setup)
def testfree():
    corsed = mw(Response(), free)
    res = preflight.get_response(corsed)
    assert res.headers.get("Access-Control-Allow-Origin", "") == "*"
    assert res.headers.get("Access-Control-Allow-Credentials", "") == "true"
    assert res.headers.get("Access-Control-Allow-Methods", "") == "post"
    assert res.headers.get("Access-Control-Allow-Headers", "") == "*"
    assert res.headers.get("Access-Control-Max-Age", "0") == "100"

    res = post.get_response(corsed)
    assert res.headers.get("Access-Control-Allow-Origin", "") == "example.com"
    assert res.headers.get("Access-Control-Allow-Credentials", "") == "true"


@with_setup(setup)
def testfree_nocred():
    """
    similar to free, but the actual request will be answered 
    with a '*' for allowed origin
    """

    corsed = mw(Response(), free_nocred)
    res = preflight.get_response(corsed)
    assert res.headers.get("Access-Control-Allow-Origin", "") == "*"
    assert res.headers.get("Access-Control-Allow-Credentials", None) == None
    assert res.headers.get("Access-Control-Allow-Methods", "") == "post"
    assert res.headers.get("Access-Control-Allow-Headers", "") == "*"
    assert res.headers.get("Access-Control-Max-Age", "0") == "100"

    res = post.get_response(corsed)
    assert res.headers.get("Access-Control-Allow-Origin", "") == "*"
    assert res.headers.get("Access-Control-Allow-Credentials", None) == None

@with_setup(setup)
def testverbatim():

    corsed = mw(Response(), verbatim)
    res = preflight.get_response(corsed)
    assert res.headers.get("Access-Control-Allow-Origin", "") == "example.com"
    assert res.headers.get("Access-Control-Allow-Credentials", "") == "true"
    assert res.headers.get("Access-Control-Allow-Methods", "") == "put,delete"
    assert res.headers.get("Access-Control-Allow-Headers", "") == "header1,header2"
    assert res.headers.get("Access-Control-Max-Age", "0") == "100"

    res = post.get_response(corsed)
    assert res.headers.get("Access-Control-Allow-Origin", "") == "example.com"
    assert res.headers.get("Access-Control-Allow-Credentials", "") == "true"

@with_setup(setup)
def test_req_origin_no_match():
    "sending a post from a disallowed host => no allow headers will be returned"

    corsed = mw(Response(), verbatim)
    res = preflight.get_response(corsed)
    assert res.headers.get("Access-Control-Allow-Origin", "") == "example.com"
    assert res.headers.get("Access-Control-Allow-Credentials", "") == "true"
    assert res.headers.get("Access-Control-Allow-Methods", "") == "put,delete"
    assert res.headers.get("Access-Control-Allow-Headers", "") == "header1,header2"
    assert res.headers.get("Access-Control-Max-Age", "0") == "100"

    res = post2.get_response(corsed)
    assert "Access-Control-Allow-Origin" not in res.headers
    assert "Access-Control-Allow-Credentials" not in res.headers

    
