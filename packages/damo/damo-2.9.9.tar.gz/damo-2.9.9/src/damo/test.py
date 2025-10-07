#!/usr/bin/env python3

import _damo_records

a, b = _damo_records.DamonStatSnapshot.capture()
print(a.to_kvpairs())
