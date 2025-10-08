class BuildInfo:

    def __init__(self, client):
        self.client = client
        self.study_type = ''
        self.subtype = ''
        self.design_type = ''
        self.design_model = ''
        self.runs = 0
        self.blocks = 0
        self.groups = 0
        self.build_time = 0
        self.center_points = 0

        result = self.client.send_payload({
            "method": "GET",
            "uri": "information/summary/build",
        })

        for k, v in result['payload'].items():
            setattr(self, k, v)


    def __str__(self):
            return """Build Information
Study Type: {study_type}
Subtype: {subtype}
Design Type: {design_type}
Design Model: {design_model}
Runs: {runs}
Blocks: {blocks}
Groups: {groups}
Build Time (ms): {build_time}
Center Points: {center_points}
Properties: {properties}""".format(
                study_type=self.study_type,
                subtype=self.subtype,
                design_type=self.design_type,
                design_model=self.design_model,
                runs=self.runs,
                blocks=self.blocks,
                groups=self.groups,
                build_time=self.build_time,
                center_points=self.center_points,
                properties=self.properties
            )
