# Frequenz Assets API

[![Build Status](https://github.com/frequenz-floss/frequenz-api-assets/actions/workflows/ci.yaml/badge.svg)](https://github.com/frequenz-floss/frequenz-api-assets/actions/workflows/ci.yaml)
[![PyPI Package](https://img.shields.io/pypi/v/frequenz-api-assets)](https://pypi.org/project/frequenz-api-assets/)
[![Docs](https://img.shields.io/badge/docs-latest-informational)](https://frequenz-floss.github.io/frequenz-api-assets/)

## Overview

The Frequenz Platform Assets API allows for the retrieval of platform assets information. Unlike CRUD-centric 
APIs, the focus here is on accessing already registered assets ranging from microgrids and gridpools to 
individual electrical components within these structures, such as sensors and their respective electrical connections.

## Objective

The main objective is to enable the building of intelligent cloud applications that can orchestrate and manage 
microgrids and gridpools for various purposes. This includes discharging batteries in a coordinated manner 
across multiple microgrids, optimizing spot market trading based on real-time grid consumption, and more.

## Key Features

- Asset Retrieval: Provides programmatic access to a wide range of platform assets, including microgrids, 
   gridpools, electrical components, and connections.
- Data-Driven Optimization: Facilitates the development of applications that can read asset information and 
   statuses for real-time decision making.
- Scheduling Insights: Enables applications to understand and adapt to gridpool schedules for improved spot 
   market trading.

## Scope and Limitations

- Retrieval of detailed asset data for various entities such as microgrids, gridpools, and their electrical components.
- Enabling advanced analytics and data-driven decisions for cloud applications.
- Read-Only: The API is designed for data retrieval and doesn't support CRUD operations for assets.
- Dependence on Platform: The quality and timeliness of data are dependent on the capabilities of the underlying platform.

## Target Audience

The API is primarily geared towards cloud application developers focused on building intelligent software 
solutions for orchestrating microgrid operations or facilitating gridpool trading. 

## Contributing

If you want to know how to build this project and contribute to it, please
check out the [Contributing Guide](CONTRIBUTING.md).
