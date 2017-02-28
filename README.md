# Azimuth-WS

The Web Service for Machine Learning-Based Predictive Modelling of CRISPR/Cas9 guide efficiency

#### Dependencies
```
pip install flask
```

```
pip install azimuth
```
#### Quick Start

```
python setup.py install
python azimuth-api.py

```
#### Usage Example

```python
http://localhost:5000/api/v1.0/prediction?sequence=CCAGAAGTTTGAGCCACAAACCCATGGTCA,CAGCTGATCTCCAGATATGACCATGGGTT

```

Output:
```JSON
[
  {
    Name: "CCAGAAGTTTGAGCCACAAACCCATGGTCA",
    OnTargets: [
      0.6452488638254855
    ]
  },
  {
    Name: "CAGCTGATCTCCAGATATGACCATGGGTTT",
    OnTargets: [
      0.6630041438744089
    ]
  }
]
```

#### Contacting us 

You can submit bug reports using the github issue tracker. 
If you have any other question please contact: azimuth@microsoft.com.
