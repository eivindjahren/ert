#!/usr/bin/env python3
import json

import numpy as np

with open("parameters.json", encoding="utf-8") as f:
    coeffs = json.load(f)["COEFFS"]
c = [np.array(coeffs["coeff_" + str(i)]) for i in range(len(coeffs))]
with open("poly.out", "w", encoding="utf-8") as f:
    f.write("\n".join(map(str, [np.polyval(c, x) for x in range(20)])))
