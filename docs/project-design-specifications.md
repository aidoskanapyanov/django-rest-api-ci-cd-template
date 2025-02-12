# 💻 Project Design Spec

## Overview

KAMI Airlines requires a RESTful API to manage and calculate fuel
consumption for 10 different airplanes.
The system will allow users to input airplane details and passenger assumptions,
and compute fuel consumption and maximum flight duration.

## Requirements

1. **Airplane Data**

   - The system must support 10 airplanes with user-defined IDs and passenger counts.
   - Each airplane has a fuel tank capacity determined by:

     `fuel_capacity = 200 * airplane_id`

   - Fuel consumption per minute is calculated as:

     `fuel_consumption = (log(airplane_id) * 0.80) + (passengers * 0.002)`

   - Maximum flight duration must be determined by:

     `max_minutes = fuel_capacity / fuel_consumption`

2. **Functionality**

   - The API must allow users to input airplane data and retrieve
     fuel consumption metrics.
   - The system must calculate total fuel consumption per minute for all airplanes.
   - The system must compute the maximum flight duration for each airplane.

3. **Project Requirements**
   - Must be implemented in Python 3.
   - Must include clear documentation and instructions.
   - Must have tests with coverage reports.
   - Code must be version-controlled using Git.
   - Design should allow future extensibility.

## Deliverables

- A working RESTful API.
- Documentation on usage and installation.
- Test cases with a high coverage score.
- Version-controlled repository with commit history.
