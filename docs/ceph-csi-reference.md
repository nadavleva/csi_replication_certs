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

| Layer 1 Test Category | Ceph Implementation | Test Function(s) | Coverage |
|------------------------|---------------------|------------------|----------|
| **1. 1.1 EnableVolumeReplication** | ✅ Partial | `TestValidateSchedulingInterval`, `TestValidateSchedulingDetails`, `TestGetSchedulingDetails` | Tests L1-E-003, L1-E-004, L1-E-005 |
| **1.1.2 DisableVolumeReplication** | ❌ Not Covered | N/A | Manual testing required |
| **1.1.3 PromoteVolume** | ✅ Partial | `Test_getCurrentReplicationStatus` (primary detection) | Tests L1-P-001 state detection only |
| **1.1.4 DemoteVolume** | ✅ Partial | `Test_getCurrentReplicationStatus` (secondary state) | Tests L1-DM-001 state detection only |
| **1.1.5 ResyncVolume** | ✅ Covered | `TestCheckVolumeResyncStatus` | Tests L1-R-001, L1-R-003 |
| **1.1.6 GetVolumeReplicationInfo** | ✅ Covered | `Test_getCurrentReplicationStatus` | Tests L1-I-001, L1-I-003 |
| **1.2 VR CRD Lifecycle** | ❌ Not Covered | N/A | Requires kubernetes-csi-addons integration tests |
| **1.3 VRC Tests** | ❌ Not Covered | N/A | Requires kubernetes-csi-addons integration tests |
| **1.4 Capability Discovery** | ❌ Not Covered | N/A | Requires CSI sidecars and controller tests |
| **1.5 Error Handling** | ✅ Covered | `TestGetGRPCError`, `TestCheckRemoteSiteStatus` | Tests L1-ERR-003, L1-ERR-005, L1-ERR-013 |
| **1.6 Performance Tests** | ❌ Not Covered | N/A | Requires dedicated performance test suite |
| **VolumeGroupSource Tests** | ❌ Not Covered | N/A | New tests - not yet implemented in Ceph |

---

## Detailed Test Function Descriptions

### 1. TestValidateSchedulingInterval
**Coverage**: L1-E-003, L1-E-005  
**Description**:  Validates scheduling interval format (3m, 22h, 13d)  
**Test Cases**:
- ✅ Valid intervals in minutes, hours, days
- ✅ Invalid intervals (missing number, missing suffix)

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
## How to Use This Reference

### For Driver Developers

1. **Study the Ceph Test Structure**:
   ```bash
   git clone https://github.com/ceph/ceph-csi. git
   cd ceph-csi
   cat internal/csi-addons/rbd/replication_test.go