from restfulgrok.fancyhtmlview import GrokRestViewWithFancyHtmlMixin


class ExampleRestViewMixin(GrokRestViewWithFancyHtmlMixin):
    def handle_get(self):
        # Return something that can be encoded by JSON and YAML
        return {'hello': 'world'}

    def handle_post(self):
        try:
            # Decode request body as a dict (JSON or YAML)
            request_data = self.get_requestdata_dict()
        except ValueError, e:
            # Did not get a dict
            return self.response_400_bad_request({'error': str(e)})
        else:
            # save to database or something....
            # --- not included in example ---

            # Respond with 201 status and the request_data
            # NOTE: If you just return normally, 200 response status is used
            return self.response_201_created(request_data)

    def handle_put(self):
        try:
            # Decode request body as a dict (JSON or YAML)
            request_data = self.get_requestdata_dict()
        except ValueError, e:
            # Did not get a dict
            return self.response_400_bad_request({'error': str(e)})
        else:
            data = request_data.copy() # pretend we got this from a database
            data['last-modified'] = 'now' # Update some data
            # would save here if this was real...

            # NOTE: If you just return normally, 200 response status is used
            return {'Updated': 'yes',
                    'result': data}
