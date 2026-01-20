# Layer 1 CSI Replication Add-on Test Cases

## Test Summary Matrix

| Test ID     | RPC Endpoint                     | Category                      | Priority | Objective                       |
|-------------|----------------------------------|-------------------------------|----------|---------------------------------|
| L1-ER-001   | /enableReplication               | Enable/Disable Replication    | High     | Ensure replication can be enabled  |
| L1-ER-002   | /disableReplication              | Enable/Disable Replication    | High     | Ensure replication can be disabled |
| L1-ER-003   | /checkReplicationStatus          | Enable/Disable Replication    | Medium   | Check current replication status   |
| L1-ER-004   | /setReplicationPolicy            | Enable/Disable Replication    | Medium   | Set a replication policy            |
| L1-ER-005   | /addReplicationTarget            | Enable/Disable Replication    | Medium   | Add a target for replication        |
| L1-ER-006   | /removeReplicationTarget         | Enable/Disable Replication    | Medium   | Remove a target from replication    |
| L1-ER-007   | /updateReplicationTarget         | Enable/Disable Replication    | Low      | Update the replication target      |
| L1-ER-008   | /listReplicationTargets          | Enable/Disable Replication    | Low      | List all replication targets       |
| L1-ER-009   | /pauseReplication                | Enable/Disable Replication    | Medium   | Pause the replication process      |
| L1-ER-010   | /resumeReplication               | Enable/Disable Replication    | Medium   | Resume the replication process     |
| L1-PV-001   | /promoteVolume                   | Promote Volume                 | High     | Promote a volume                   |
| L1-PV-002   | /getVolumeStatus                 | Promote Volume                 | Medium   | Verify the volume status           |
| L1-PV-003   | /promoteVolumeStatus             | Promote Volume                 | Medium   | Check the status of promoted volume |
| L1-PV-004   | /rollbackVolume                  | Promote Volume                 | Medium   | Rollback a promoted volume         |
| L1-PV-005   | /resizeVolume                    | Promote Volume                 | Low      | Resize promoted volume             |
| L1-PV-006   | /promoteAndValidate              | Promote Volume                 | High     | Promote and validate volume        |
| L1-PV-007   | /listPromotedVolumes             | Promote Volume                 | Low      | List all promoted volumes          |
| L1-PV-008   | /clearPromotedVolume             | Promote Volume                 | Low      | Clear promoted volume              |
| L1-DV-001   | /demoteVolume                    | Demote Volume                  | High     | Demote a volume                   |
| L1-DV-002   | /getDemoteVolumeStatus           | Demote Volume                  | Medium   | Verify the demote volume status    |
| L1-DV-003   | /demoteAndValidate               | Demote Volume                  | High     | Demote and validate volume        |
| L1-DV-004   | /listDemotedVolumes              | Demote Volume                  | Low      | List demoted volumes               |
| L1-DV-005   | /rollbackDemotedVolume           | Demote Volume                  | Low      | Rollback demoted volume            |
| L1-DV-006   | /clearDemotedVolume              | Demote Volume                  | Low      | Clear demoted volume               |
| L1-DV-007   | /checkDemoteVolumeError          | Demote Volume                  | Medium   | Check error on demote volume       |
| L1-DV-008   | /getDemoteVolumeResult           | Demote Volume                  | Medium   | Get the result of a demote volume  |
| L1-RV-001   | /resyncVolume                    | Resync Volume                  | High     | Resync a volume                   |
| L1-RV-002   | /getResyncStatus                 | Resync Volume                  | Medium   | Check the status of resync        |
| L1-RV-003   | /forceResync                     | Resync Volume                  | Medium   | Force a volume to resync           |
| L1-RV-004   | /validateResync                  | Resync Volume                  | Medium   | Validate the resync process       |
| L1-RV-005   | /retryResync                     | Resync Volume                  | Low      | Retry the resync process          |
| L1-RV-006   | /listResyncVolumes               | Resync Volume                  | Low      | List all resync volumes            |
| L1-RV-007   | /clearResyncStatus               | Resync Volume                  | Low      | Clear resync status                 |
| L1-RI-001   | /getReplicationInfo              | Get Replication Info           | High     | Retrieve replication info           |
| L1-RI-002   | /listReplicationInfo             | Get Replication Info           | Medium   | List all replication info           |
| L1-RI-003   | /checkReplicationInfo            | Get Replication Info           | Medium   | Check the replication info         |
| L1-RI-004   | /validateReplicationInfo          | Get Replication Info           | Medium   | Validate the replication info        |
| L1-EH-001   | /handleReplicationError          | Error Handling                 | High     | Handle an error in replication      |
| L1-EH-002   | /getErrorCodes                   | Error Handling                 | Medium   | Retrieve error codes                |
| L1-EH-003   | /logReplicationError             | Error Handling                 | Medium   | Log a replication error            |
| L1-EH-004   | /retryOnError                    | Error Handling                 | Low      | Retry replication on error         |
| L1-EH-005   | /testErrorResponse               | Error Handling                 | Medium   | Test error responses               |

## Test Execution Guide
1. Set up the environment and ensure all prerequisites are met.
2. Execute each test case in the specified order, using the appropriate RPC endpoint.
3. Monitor the system and log all outputs and responses.
4. Compare the actual results with the expected results as listed in the test matrix.

## Success Criteria
- Each test must execute without errors, returning the expected results.
- Document any deviations and discrepancies in the results.
- All tests must pass within the allocated execution time.

## Troubleshooting
- If a test fails, check the prerequisites and specified setup.
- Review error logs for relevant error messages and codes.
- Verify that all RPC endpoints are reachable and functioning as expected.

## References
- [CSI Add-ons Specification](https://github.com/kubernetes-sigs/csi-addons/spec)
- [KubeVirt Storage Checkup API Summary](https://github.com/kubevirt/kubevirt-storage-checkup)
