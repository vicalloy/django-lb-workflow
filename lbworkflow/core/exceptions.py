class HttpResponseException(Exception):
    def __init__(self, http_response):
        super(HttpResponseException, self).__init__(http_response)
        self.http_response = http_response
