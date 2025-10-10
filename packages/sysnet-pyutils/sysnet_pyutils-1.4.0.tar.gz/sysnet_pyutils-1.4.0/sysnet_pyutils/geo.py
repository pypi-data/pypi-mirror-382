import math


class JTSK:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def from_wgs84(self, lon: float, lat: float, alt: float = float(200)):
        d2r = math.pi / 180
        a = 6378137.0
        f1 = 298.257223563
        dx = -570.69
        dy = -85.69
        dz = -462.84
        wx = 4.99821 / 3600 * math.pi / 180
        wy = 1.58676 / 3600 * math.pi / 180
        wz = 5.2611 / 3600 * math.pi / 180
        m = -3.543e-6

        b_cap = lat * d2r
        l_cap = lon * d2r
        h_cap = alt

        e2 = 1 - math.pow(1 - 1 / f1, 2)
        rho = a / math.sqrt(1 - e2 * math.pow(math.sin(b_cap), 2))
        x1 = (rho + h_cap) * math.cos(b_cap) * math.cos(l_cap)
        y1 = (rho + h_cap) * math.cos(b_cap) * math.sin(l_cap)
        z1 = ((1 - e2) * rho + h_cap) * math.sin(b_cap)

        x2 = dx + (1 + m) * (x1 + wz * y1 - wy * z1)
        y2 = dy + (1 + m) * (-wz * x1 + y1 + wx * z1)
        z2 = dz + (1 + m) * (wy * x1 - wx * y1 + z1)

        a = 6377397.15508
        f1 = 299.152812853
        ab = f1 / (f1 - 1)
        p = math.sqrt(math.pow(x2, 2) + math.pow(y2, 2))
        e2 = 1 - math.pow(1 - 1 / f1, 2)
        th = math.atan(z2 * ab / p)
        st = math.sin(th)
        ct = math.cos(th)
        t = (z2 + e2 * ab * a * (st * st * st)) / (p - e2 * a * (ct * ct * ct))

        b_cap = math.atan(t)
        h_cap = math.sqrt(1 + t * t) * (p - a / math.sqrt(1 + (1 - e2) * t * t))
        l_cap = 2 * math.atan(y2 / (p + x2))

        a = 6377397.15508
        e = 0.081696831215303
        n = 0.97992470462083
        rho0 = 12310230.12797036
        sin_uq = 0.863499969506341
        cos_uq = 0.504348889819882
        sin_vq = 0.420215144586493
        cos_vq = 0.907424504992097
        alpha = 1.000597498371542
        k2 = 1.00685001861538

        sin_b = math.sin(b_cap)
        t = (1 - e * sin_b) / (1 + e * sin_b)
        t = math.pow(1 + sin_b, 2) / (1 - math.pow(sin_b, 2)) * math.exp(e * math.log(t))
        t = k2 * math.exp(alpha * math.log(t))

        sin_u = (t - 1) / (t + 1)
        cos_u = math.sqrt(1 - sin_u * sin_u)
        v_cap = alpha * l_cap
        sin_v = math.sin(v_cap)
        cos_v = math.cos(v_cap)
        cos_dv = cos_vq * cos_v + sin_vq * sin_v
        sin_dv = sin_vq * cos_v - cos_vq * sin_v
        sin_s = sin_uq * sin_u + cos_uq * cos_u * cos_dv
        cos_s = math.sqrt(1 - sin_s * sin_s)
        sin_d = sin_dv * cos_u / cos_s
        cos_d = math.sqrt(1 - sin_d * sin_d)

        eps = n * math.atan(sin_d / cos_d)
        rho = rho0 * math.exp(-n * math.log((1 + sin_s) / cos_s))

        cx = rho * math.sin(eps)
        cy = rho * math.cos(eps)

        self.x = -cx
        self.y = -cy

        return self


class Wgs84:
    def __init__(self, latitude: float, longitude: float, altitude=float(200)):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
