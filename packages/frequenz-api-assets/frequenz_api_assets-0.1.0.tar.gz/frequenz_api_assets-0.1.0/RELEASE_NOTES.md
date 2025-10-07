# Frequenz Assets API Release Notes

## Summary

This release updates the Frequenz Assets API to align with the new naming conventions and the latest version of the common API (v1alpha8). The changes include renaming RPC methods and message types to be more explicit about electrical components, as well as updating dependencies to ensure compatibility with the latest API specifications.

## Upgrading

⚠️ **Breaking Changes** - This release contains API changes that will require updates to client code:

### API Changes

1. **RPC Method Renaming** - All RPC methods related to microgrid components have been renamed to explicitly include "Electrical" in their names:
   - `ListMicrogridComponents` → `ListMicrogridElectricalComponents`
   - `ListMicrogridComponentConnections` → `ListMicrogridElectricalComponentConnections`

2. **Message Type Renaming** - Corresponding request and response message types have also been renamed:
   - `ListMicrogridComponentsRequest` → `ListMicrogridElectricalComponentsRequest`
   - `ListMicrogridComponentsResponse` → `ListMicrogridElectricalComponentsResponse`
   - `ListMicrogridComponentConnectionsRequest` → `ListMicrogridElectricalComponentConnectionsRequest`
   - `ListMicrogridComponentConnectionsResponse` → `ListMicrogridElectricalComponentConnectionsResponse`

3. **Common API Update** - Proto imports have been updated from `frequenz.api.common.v1` to `frequenz.api.common.v1alpha8`. This affects:
   - `frequenz.api.common.v1alpha8.microgrid.electrical_components.ElectricalComponent`
   - `frequenz.api.common.v1alpha8.microgrid.electrical_components.ElectricalComponentCategory`
   - `frequenz.api.common.v1alpha8.microgrid.electrical_components.ElectricalComponentConnection`
   - `frequenz.api.common.v1alpha8.microgrid.Microgrid`

### Migration Steps

1. Update your `frequenz-api-common` dependency to v1alpha8 or later
2. Update all RPC method calls to use the new `*ElectricalComponent*` naming
3. Update all message type references to match the new naming convention
4. Update proto imports from `v1` to `v1alpha8` for common API types
5. Regenerate your protobuf stubs with the updated proto files

### Dependency Updates

- Updated `protobuf` and `grpcio` versions for improved compatibility
- Updated `frequenz-api-common` submodule to the latest commit
- Updated development dependencies including `pydoclint` (0.6.0 → 0.6.6) and various patch-level updates

## New Features

This release focuses primarily on alignment with the new naming conventions and API standards. The core functionality remains the same, with the following service methods available:

- `GetMicrogrid` - Fetch details about a specific microgrid
- `ListMicrogridElectricalComponents` - List electrical components for a specific microgrid with optional filtering by component IDs and categories
- `ListMicrogridElectricalComponentConnections` - List connections between electrical components in a microgrid

## Bug Fixes

No significant bug fixes in this release. The changes are primarily focused on API alignment and naming consistency.
