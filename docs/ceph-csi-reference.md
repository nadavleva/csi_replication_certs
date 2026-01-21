# Ceph CSI Driver Reference Implementation

This document provides a detailed mapping of how the Ceph CSI driver implements Layer 1 CSI Replication Add-on tests.  Use this as a reference for implementing tests in other CSI drivers.

---

## Overview

The Ceph CSI driver provides a reference implementation for many Layer 1 tests, covering approximately 25% of the test suite at the unit test level. This document maps Layer 1 test cases to Ceph's implementation. 

---

## Ceph CSI Test Location

📁 **Repository**: https://github.com/ceph/ceph-csi  
📄 **Test File**: `internal/csi-addons/rbd/replication_test.go`  
🔗 **Direct Link**: [replication_test.go](https://github.com/ceph/ceph-csi/blob/devel/internal/csi-addons/rbd/replication_test.go)

---

## Test Coverage Mapping

### CSI gRPC Endpoint Tests (layer-1-vr-tests.md)

| Layer 1 Test Category | Ceph Implementation | Test Function(s) | Coverage |
|------------------------|---------------------|------------------|----------|
| **EnableVolumeReplication** | ✅ Partial | `TestValidateSchedulingInterval`, `TestValidateSchedulingDetails`, `TestGetSchedulingDetails` | Tests L1-E-004, L1-E-005 (parameter validation) |
| **DisableVolumeReplication** | ❌ Not Covered | N/A | Tests L1-DIS-001 through L1-DIS-008 - Manual testing required |
| **PromoteVolume** | ✅ Partial | `Test_getCurrentReplicationStatus` (primary detection) | State detection only - needs L1-P-001 through L1-P-006 scenarios |
| **DemoteVolume** | ✅ Partial | `Test_getCurrentReplicationStatus` (secondary state) | State detection only - needs L1-DEM-001 through L1-DEM-006 scenarios |
| **ResyncVolume** | ✅ Covered | `TestCheckVolumeResyncStatus` | Tests L1-R-001, L1-R-003 (basic resync status) |
| **GetVolumeReplicationInfo** | ✅ Covered | `Test_getCurrentReplicationStatus` | Tests L1-I-001, L1-I-003 (status retrieval) |
| **Error Handling** | ✅ Covered | `TestGetGRPCError`, `TestCheckRemoteSiteStatus` | gRPC error mapping and remote site status checks |
| **Capability Discovery** | ❌ Not Covered | N/A | Requires CSI sidecars and controller tests |
| **Performance Tests** | ❌ Not Covered | N/A | Requires dedicated performance test suite |

### VRG API Tests (layer-1-vrg-tests.md)

| VRG Test Category | Ceph Implementation | Test Function(s) | Coverage |
|-------------------|---------------------|------------------|----------|
| **VRG Disable Operations** | ❌ Not Covered | N/A | Tests L1-VRG-DIS-001 through L1-VRG-DIS-016 - Not implemented in Ceph |
| **VRG Create/Delete** | ❌ Not Covered | N/A | Tests L1-VRG-CREATE-001 through L1-VRG-DELETE-004 - Requires kubernetes-csi-addons |
| **VRG Failover/Failback** | ❌ Not Covered | N/A | Tests L1-VRG-FAIL-001 through L1-VRG-BACK-004 - Requires multi-cluster setup |
| **VRG S3 Integration** | ❌ Not Covered | N/A | S3 metadata handling - Not implemented in Ceph |
| **VRG Status/Monitoring** | ❌ Not Covered | N/A | Health checks and sync status - Requires kubernetes-csi-addons |

---

## Detailed Test Function Descriptions

### 1. TestValidateSchedulingInterval
**Coverage**: L1-E-004, L1-E-005  
**Description**:  Validates scheduling interval format (3m, 22h, 13d)  
**Test Cases**:
- ✅ Valid intervals in minutes, hours, days (L1-E-001, L1-E-002)
- ✅ Invalid intervals (missing number, missing suffix) (L1-E-004)
- ❌ Missing: Peer connectivity scenarios (L1-E-003, L1-E-006)

**Example Test**:
```go
func TestValidateSchedulingInterval(t *testing.T) {
    tests := []struct {
        interval string
        valid    bool
    }{
        {"3m", true},
        {"22h", true},
        {"13d", true},
        {"5x", false},
        {"", false},
    }
    // ... 
}

```markdown
## Layer-1 Test Structure Overview

The Layer-1 test plan has been significantly expanded and restructured:

### CSI gRPC Endpoint Tests (`layer-1-vr-tests.md`)
- **EnableVolumeReplication**: 6 scenarios (L1-E-001 to L1-E-006)
- **DisableVolumeReplication**: 8+ scenarios (L1-DIS-001 to L1-DIS-008+) covering all state permutations
- **PromoteVolume**: 6+ scenarios (L1-P-001 to L1-P-006+) with force parameters
- **DemoteVolume**: 6+ scenarios (L1-DEM-001 to L1-DEM-006+) with force parameters  
- **ResyncVolume**: Multiple scenarios including split-brain recovery
- **GetVolumeReplicationInfo**: Status and sync information retrieval

### VRG API Tests (`layer-1-vrg-tests.md`)
- **VRG Disable Operations**: 16 core scenarios (L1-VRG-DIS-001 to L1-VRG-DIS-016)
  - Active/Previously disabled states
  - Peer up/down connectivity
  - Array up/down states  
  - force=true/false parameters
- **VRG Lifecycle**: Create, delete, failover, failback operations
- **VRG S3 Integration**: Metadata handling and S3 unavailable scenarios

### Test Coverage Gaps in Ceph CSI
The Ceph CSI driver currently covers **~15-20%** of the expanded test matrix:
- ✅ **Covered**: Parameter validation, basic status checks, error handling
- ⚠️ **Partial**: State detection without full workflow testing
- ❌ **Missing**: VRG operations, comprehensive disable scenarios, multi-cluster workflows

---

## How to Use This Reference

### For Driver Developers

1. **Study the Ceph Test Structure**:
   ```bash
   git clone https://github.com/ceph/ceph-csi.git
   cd ceph-csi
   cat internal/csi-addons/rbd/replication_test.go
   ```

2. **Focus on Coverage Gaps**:
   - **High Priority**: Implement L1-DIS-001 through L1-DIS-008 (DisableVolumeReplication scenarios)
   - **Medium Priority**: Complete L1-P-001+ and L1-DEM-001+ (Promote/Demote with force parameters)
   - **Low Priority**: VRG operations (requires kubernetes-csi-addons integration)

3. **Reference Test Mapping**:
   - Use the detailed test IDs from `layer-1-vr-tests.md` for CSI gRPC endpoint tests
   - Use test IDs from `layer-1-vrg-tests.md` for VRG API workflow tests
   - Map your driver's test functions to the standardized Layer-1 test IDs

### For Test Framework Authors

1. **Implement Missing Scenarios**:
   ```go
   // Example: L1-DIS-005 (Peer down, force=false)
   func TestDisableVolumeReplication_PeerDown_NoForce(t *testing.T) {
       // Simulate peer connectivity failure
       // Call DisableVolumeReplication with force=false
       // Expect: Operation fails gracefully with appropriate error
   }
   ```

2. **VRG Test Implementation**:
   - VRG tests require kubernetes-csi-addons controller
   - Focus on comprehensive state matrix testing
   - Include S3 metadata scenarios for complete coverage

### For Certification Bodies

1. **Coverage Assessment**:
   - Ceph CSI: ~15-20% coverage (primarily parameter validation)
   - Gap Analysis: Missing comprehensive workflow and negative testing
   - VRG Operations: Requires separate test framework

2. **Certification Requirements**:
   - **Minimum**: Cover all L1-E-*, L1-DIS-*, L1-P-*, L1-DEM-*, L1-R-*, L1-I-* scenarios
   - **Recommended**: Include L1-VRG-* scenarios for complete Layer-1 certification
   - **Performance**: Implement dedicated performance test suite per requirements
   ```

2. **Focus on Coverage Gaps**:
   - **High Priority**: Implement L1-DIS-001 through L1-DIS-008 (DisableVolumeReplication scenarios)
   - **Medium Priority**: Complete L1-P-001+ and L1-DEM-001+ (Promote/Demote with force parameters)
   - **Low Priority**: VRG operations (requires kubernetes-csi-addons integration)

3. **Reference Test Mapping**:
   - Use the detailed test IDs from `layer-1-vr-tests.md` for CSI gRPC endpoint tests
   - Use test IDs from `layer-1-vrg-tests.md` for VRG API workflow tests
   - Map your driver's test functions to the standardized Layer-1 test IDs

### For Test Framework Authors

1. **Implement Missing Scenarios**:
   ```go
   // Example: L1-DIS-005 (Peer down, force=false)
   func TestDisableVolumeReplication_PeerDown_NoForce(t *testing.T) {
       // Simulate peer connectivity failure
       // Call DisableVolumeReplication with force=false
       // Expect: Operation fails gracefully with appropriate error
   }
   ```

2. **VRG Test Implementation**:
   - VRG tests require kubernetes-csi-addons controller
   - Focus on comprehensive state matrix testing
   - Include S3 metadata scenarios for complete coverage

### For Certification Bodies

1. **Coverage Assessment**:
   - Ceph CSI: ~15-20% coverage (primarily parameter validation)
   - Gap Analysis: Missing comprehensive workflow and negative testing
   - VRG Operations: Requires separate test framework

2. **Certification Requirements**:
   - **Minimum**: Cover all L1-E-*, L1-DIS-*, L1-P-*, L1-DEM-*, L1-R-*, L1-I-* scenarios
   - **Recommended**: Include L1-VRG-* scenarios for complete Layer-1 certification
   - **Performance**: Implement dedicated performance test suite per requirements