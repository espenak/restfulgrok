from restfulgrok import GrokRestViewMixin


class ExampleRestViewMixin(GrokRestViewMixin):
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
