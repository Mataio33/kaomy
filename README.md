\# Kaomy



<p align="center">



<img src="docs/logo.png" width="180">



\*\*Home Resource Framework for Home Assistant\*\*



Persistent • Modular • Provider Agnostic • AppDaemon Powered



</p>



\---



\## Overview



Kaomy is a lightweight framework designed to collect, normalize, cache and publish home resource data for Home Assistant.



Instead of writing one script per provider, Kaomy introduces a modular architecture separating:



\- Providers

\- Collectors

\- Cache

\- Home Assistant publication



This makes adding new providers and new resources extremely simple.



\---



\## Features



\- Persistent local cache

\- Automatic restoration after Home Assistant restart

\- Automatic restoration after AppDaemon restart

\- Provider / Collector architecture

\- Home Assistant sensor publishing

\- ApexCharts-compatible historical data

\- Energy Dashboard compatible sensors

\- Clean Python architecture

\- Fully documented

\- Easily extensible



\---



\## Current Providers



| Provider | Resource |

|----------|----------|

| CDE | Water |

| Enercal | Electricity |



\---



\## Current Collectors



| Collector | Resource |

|-----------|----------|

| water\_principal | Main water meter |

| power\_maison | House electricity |



\---



\## Project Architecture



```text

kaomy/

│

├── cache/

│

├── collectors/

│   ├── power\_maison.py

│   └── water\_principal.py

│

├── core/

│   ├── banner.py

│   ├── cache\_manager.py

│   ├── constants.py

│   ├── exceptions.py

│   └── sensor\_manager.py

│

├── docs/

│

├── models/

│   ├── resource\_metadata.py

│   └── resource\_state.py

│

├── providers/

│   ├── base\_provider.py

│   ├── cde.py

│   └── enercal.py

│

├── README.md

├── LICENSE

└── version.py

```



\---



\## How it works



```text

&#x20;         External Provider

&#x20;                │

&#x20;                ▼

&#x20;           Provider

&#x20;                │

&#x20;                ▼

&#x20;         ResourceState

&#x20;                │

&#x20;       ┌────────┴────────┐

&#x20;       │                 │

&#x20;       ▼                 ▼

&#x20;  CacheManager     SensorManager

&#x20;       │                 │

&#x20;       └────────┬────────┘

&#x20;                ▼

&#x20;         Home Assistant

```



\---



\## Home Assistant



Kaomy automatically creates compatible sensors for:



\- Home Assistant Recorder

\- Home Assistant Statistics

\- Home Assistant Energy Dashboard

\- ApexCharts



\---



\## Example AppDaemon configuration



```yaml

power\_maison:

&#x20; module: kaomy.collectors.power\_maison

&#x20; class: PowerMaisonCollector



&#x20; username: CHANGE\_ME

&#x20; password: CHANGE\_ME



&#x20; schedule: "03:00:00"



&#x20; simulation: false





water\_principal:

&#x20; module: kaomy.collectors.water\_principal

&#x20; class: WaterPrincipalCollector



&#x20; username: CHANGE\_ME

&#x20; password: CHANGE\_ME



&#x20; point\_installation\_id: CHANGE\_ME



&#x20; schedule: "02:00:00"



&#x20; simulation: false

```



\---



\# CDE - Finding the point\_installation\_id



To retrieve the \*\*point\_installation\_id\*\*:



1\. Login to the CDE customer portal.

2\. Open the \*\*Consumption\*\* page.

3\. Open the browser \*\*Developer Tools\*\*.

4\. Go to the \*\*Network\*\* tab.

5\. Refresh the consumption graph.

6\. Locate the request named:



```text

GetGraphRelevesData

```



7\. Inspect the request payload.



You will find:



```text

pointDInstallationId

```



Example:



```text

76543

```



Use this value in \*\*apps.yaml\*\*.



\---



\# Running a collector immediately



Collectors normally run once per day.



Example:



```yaml

schedule: "03:00:00"

```



During development or testing you can trigger an immediate execution.



Temporarily uncomment the following line inside the collector:



```python

self.run\_in(self.collect\_and\_publish, 10)

```



Example:



```text

collectors/power\_maison.py

collectors/water\_principal.py

```



The collector will execute \*\*10 seconds\*\* after AppDaemon starts.



Once the cache has been created successfully, remove or comment the line again.



This avoids unnecessary requests to external providers.



\---



\## Security



Do \*\*NOT\*\* commit:



```text

apps.yaml

cache/\*.json

```



Credentials must remain inside your AppDaemon configuration.



\---



\## Screenshot



!\[Kaomy Dashboard](docs/screenshot-dashboard.png)



\---



\## Roadmap



\### Version 1.0



\- \[x] CacheManager

\- \[x] SensorManager

\- \[x] ResourceState

\- \[x] ResourceMetadata

\- \[x] Enercal Provider

\- \[x] CDE Provider

\- \[x] Main electricity collector

\- \[x] Main water collector



\### Next



\- Consumption analytics

\- Cost analytics

\- Solar production

\- Battery storage

\- Weather integration

\- Smart recommendations



\---



\## License



MIT



\---



\## Author



Created by \*\*Mataïo\*\*





\---



\## Philosophy



Kaomy follows one simple rule:



> \*\*Providers collect data.\*\*



> \*\*Collectors orchestrate.\*\*



> \*\*The Core remains provider agnostic.\*\*



This philosophy keeps Kaomy modular, testable and easy to extend.



