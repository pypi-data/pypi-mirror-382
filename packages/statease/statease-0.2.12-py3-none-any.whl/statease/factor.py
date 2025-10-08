class Factor:
    """Factor

The Factor class holds information about an individual Factor in
Stat-Ease 360. Instances of this class are typically created by
:func:`statease.client.SEClient.get_factor`

Attributes:
    name (str): the name of the factor

    units (str): the units of the factor

    values (tuple): the values of the factor, in run order

    low (str, **read only**): the actual low that corresponds to the *coded* low (this is usually, but not necessarily, the minimum observed value)

    high (str, **read only**): the actual high that corresponds to the *coded* high (this is usually, but not necessarily, the maximum observed value)

    coded_low (str, **read only**): the coded low value, typically -1 or 0

    coded_high (str, **read only**): the coded high value, typically 1
"""

    def __init__(self, client = None, name = "", **kwargs):
        self.__name = name
        self.__client = client
        self.__is_block = kwargs.get('is_block', False)
        if client:
            self.get()
        else:
            self.from_dict(kwargs)

    def __str__(self):
        return 'name: "{}"\nunits: "{}"\nvariable_id:"{}"\ntype: "{}" subtype: "{}"\ncoded low: {} <-> {}\ncoded high: {} <-> {}\nis_categorical: {}'.format(
            self.__name,
            self.__units,
            self.__variable_id,
            self.__type,
            self.__subtype,
            self.__levels[0],
            self.__coded_low,
            self.__levels[-1],
            self.__coded_high,
            self.__is_categorical,
        )

    def get(self):
        if self.__is_block:
            uri = "design/block"
        else:
            uri = "design/factor/" + self.__name
        result = self.__client.send_payload({
            "method": "GET",
            "uri": uri,
        })

        self.from_dict(result['payload'])

    def post(self, endpoint, payload):
        return self.__client.send_payload({
            "method": "POST",
            "uri": "design/factor/{}/{}".format(self.__name, endpoint),
            **payload,
        })

    def from_dict(self, data):
        self.__name = data.get('name', self.__name)
        self.__variable_id = data.get('variable_id',None)
        self.__units = data.get('units', '')
        self.__type = data.get('type', '')
        self.__subtype = data.get('subtype', '')
        self.__changes = data.get('changes', 'easy')
        self.__values = tuple(data.get('values', []))
        self.__coded_low = data.get('coded_low', None)
        self.__coded_high = data.get('coded_high', None)
        self.__coded_values = tuple(data.get('coded_values', []))
        self.__is_block = data.get('is_block', None)
        self.__contrasts = tuple(data.get('contrasts', []))

        self.__is_categorical = data.get('is_categorical', None)
        self.__levels = data.get('levels', [])
        if len(self.__levels) > 2:
            self.__is_categorical = True
            self.__type = 'categoric'

        if len(self.__levels) < 2:
            self.__levels = [ None, None ]
            if data.get('actual_low', None) is not None:
                self.__levels[0] = data['actual_low']
            elif data.get('low', None) is not None:
                self.__levels[0] = data['low']

            if data.get('actual_high', None) is not None:
                self.__levels[-1] = data['actual_high']
            elif data.get('high', None) is not None:
                self.__levels[-1] = data['high']

        if self.__is_categorical:
            # Convert inner nested lists to tuples for efficiency
            self.__levels = tuple(self.__levels)
            if not isinstance(self.__coded_values, tuple):
                self.__coded_values = tuple([ tuple(sublist) if sublist is not None else None for sublist in self.__coded_values])

    def to_dict(self):
        data = {}
        data["name"] = self.name
        data["units"] = self.units
        data["type"] = self.type
        data["column_type"] = self.type
        data["changes"] = self.changes
        data["actual_low"] = self.actual_low
        data["actual_high"] = self.actual_high
        data["levels"] = self.levels
        data["is_categorical"] = self.is_categorical
        return data;

    @property
    def name(self):
        return self.__name

    @property
    def variable_id(self):
        return self.__variable_id

    @property
    def units(self):
        return self.__units

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, factor_type):
        self.__type = factor_type

    @property
    def subtype(self):
        return self.__subtype

    @property
    def changes(self):
        return self.__changes

    @property
    def coded_high(self):
        return self.__coded_high

    @property
    def coded_low(self):
        return self.__coded_low

    @property
    def low(self):
        return self.__levels[0]

    @low.setter
    def low(self, low):
        self.__levels[0] = low

    @property
    def high(self):
        return self.__levels[-1]

    @high.setter
    def high(self, high):
        self.__levels[-1] = high

    @property
    def actual_low(self):
        return self.__levels[0]

    @property
    def actual_high(self):
        return self.__levels[-1]

    @property
    def values(self):
        """Get or set the factor values. When setting the factor values, you may use
        either a list or a dictionary. If fewer values are assigned than there are rows
        in the design, they will be filled in starting with first row. If a dictionary
        is used, it must use integers as keys, and it will fill factor values in rows
        indexed by the dictionary keys. The indices are 0-based, so the first row is
        index 0, the second index 1, and so on.

        :Example:
            >>> # sets the first 4 rows to a list of values
            >>> factor.values = [.1, .2, .3, .4]
            >>> # sets the 7th through 10th rows to specific values
            >>> factor.values = { 6: .1, 7: .2, 8: .3, 9: .4 }
            >>> # sets the 6th run to a specific value
            >>> factor.values = { 5: .8 }
        """
        return self.__values

    @values.setter
    def values(self, factor_values):
        result = self.post("set", {"factor_values": factor_values })
        self.__values = tuple(result['payload']['values'])
        self.__coded_values = tuple(result['payload']['coded_values'])
        self.__coded_high = result['payload'].get('coded_high', 1)
        self.__coded_low = result['payload'].get('coded_low', -1)
        self.__levels = [
            result['payload'].get('actual_low', -1),
            result['payload'].get('actual_high', 1)
        ]

    @property
    def coded_values(self):
        """Get the coded factor values in the current coding.

        :Example:
            >>> # get a list of the coded values
            >>> xc = factor.coded_values
        """
        return self.__coded_values

    @property
    def is_block(self):
        return self.__is_block

    @property
    def levels(self):
        return self.__levels

    @levels.setter
    def levels(self, levels_values):
        self.__levels = list(levels_values)
        if self.__client:
            self.post("setlevels", {"levels_values" : levels_values})

    @property
    def contrasts(self):
        return self.__contrasts

    @property
    def is_categorical(self):
      """Test for categorical factor type.

        :Example:
            >>> # get a list of the coded values
            >>> #  values if the factor is categorical
            >>> x = []
            >>> if (factor.is_categorical):
            >>>   x = factor.coded_values
            >>> else: # Factor is not categorical
            >>>   x = factor.values
        """
      return self.__is_categorical
