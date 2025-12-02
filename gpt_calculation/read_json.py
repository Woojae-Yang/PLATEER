#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  2 15:41:07 2025

@author: ywj
"""

import pandas as pd

df = pd.read_json('kje.json')
print(df.head(50))