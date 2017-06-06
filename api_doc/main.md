# Opendata API Documentation


## [ToxicHeaveyGasDispersionPlumeModel](https://github.com/paradigmC/opendata-falcon-app/tree/master/app/resources/toxic_heavy_gas_dispersion)

There are two model [Puff](https://github.com/paradigmC/opendata-falcon-app/blob/master/app/resources/toxic_heavy_gas_dispersion/toxicHeavyGasDispersionPuffModel.py) and [Plume](https://github.com/paradigmC/opendata-falcon-app/blob/master/app/resources/toxic_heavy_gas_dispersion/toxicHeavyGasDispersionPlumeModel.py) which are taking [BMM-Curve-Approximation](https://github.com/paradigmC/opendata-falcon-app/blob/master/app/resources/toxic_heavy_gas_dispersion/bmmCurveApproximation.py)

------
### Puff

#### Request

**Endpoint**

http://HOST/thgd/puff

**Header**

```
Content-Type:application/json
Authorization:Basic <Encrypted-Key>
```

**Body**

```javascript
{
  "gas_name": "MIC",
  "wind_speed": 1.9,
  "initial_concentration": 6,
  "source_radius": 2,
  "instantaneous_release": 4000
}
```

------

#### Response

```javascript
[
  {
    "ratio": 0.1,
    "yValue": -1,
    "cmax": 0.6,
    "x": -15.8740105197,
    "t": 0.0379364354,
    "b": -15.9028422106,
    "bz": 50.3454954279
  },
  {
    "ratio": 0.05,
    "yValue": -1,
    "cmax": 0.3,
    "x": -15.8740105197,
    "t": 0.0379364354,
    "b": -15.9028422106,
    "bz": 100.6909908558
  }
  ...
]
```


------
### Plume

#### Request

**Endpoint**

http://HOST/thgd/plume

**Header**

```
Content-Type:application/json
Authorization:Basic <Encrypted-Key>
```

**Body**

```javascript
{
  "gas_name": "LP",
  "wind_speed": 4,
  "initial_concentration": 6,
  "dispersion_volume": 1,
  "source_radius": 2
}
```
------

#### Response

```javascript
[
  {
    "ratio": 0.1,
    "yValue": 22.8912611875,
    "cmax": 0.6,
    "x": 11.4456305938,
    "b": 560.0602568697,
    "bz": 0.0002231903
  },
  {
    "ratio": 0.05,
    "yValue": 30.8482184129,
    "cmax": 0.3,
    "x": 15.4241092065,
    "b": 571.1879686284,
    "bz": 0.0002188421
  },
  ...
]
```
