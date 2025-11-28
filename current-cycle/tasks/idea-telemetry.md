# Telemetry Feature Design

## Original Requirements

Implement telemetry data export for thrift services with the following features:

- Counter system with key=int where keys are a thrift enum
- Thread-safe atomic value increments
- BaseService endpoint to fetch current snapshot of counter values
- Default counters:
  - Bytes received by service
  - Bytes sent by service
  - Number of successful requests
  - Number of error requests
- API: `def increment_counter(key, amount_of_increase)` for thread-safe increments
- Counter management class that runs in its own thread at service startup
- Singleton counter class with lockable data for atomic writes
- Non-atomic reads acceptable (endpoint queried every 30-60 seconds)
- Integration test that:
  - Spins up service instance on specific port
  - Accesses telemetry endpoint
  - Validates counter increases
  - Sends both valid and invalid requests to verify counter updates

## Current Architecture Analysis

### Service Structure

- Services inherit from `BaseServiceHandler` which implements thrift `BaseService` interface
- Each service (ItemService, InventoryService, PlayerService) runs in a separate **process** (not thread)
- Services use `TSimpleServer` which is **single-threaded and blocking**
- Server code location: `/vagrant/gamedb/thrift/py/run_servers.py`
- Testing pattern: unit tests instantiate handlers directly; integration tests would need actual service instances

### Critical Discovery: Single-Threaded Blocking Services

**PROBLEM IDENTIFIED**: Services currently use `TServer.TSimpleServer` which:
- Handles one request at a time (blocking)
- Cannot handle concurrent requests
- Not suitable for production or telemetry with background threads

**Location**: `/vagrant/gamedb/thrift/py/run_servers.py:84, 114, 144`

```python
server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
```

## Required Pre-Work: Fix Server Threading Model

**MUST DO FIRST**: Update services to use multi-threaded, non-blocking server before implementing telemetry.

### Options for Threading:

1. **TThreadedServer** - Creates new thread per connection
2. **TThreadPoolServer** - Thread pool for handling requests
3. **TNonblockingServer** - Async I/O (requires different transport)

### Recommendation: TThreadPoolServer

```python
from thrift.server.TServer import TThreadPoolServer

server = TThreadPoolServer(
    processor,
    transport,
    tfactory,
    pfactory,
    daemon=True,
)
```

**Reasoning**:
- Bounded resource usage (vs unlimited threads)
- Better performance under load
- Compatible with current transport setup
- Allows concurrent request handling + background telemetry thread

## Telemetry Design - Three Approaches

### Approach 1: Thread-Safe Counter Class with threading.Lock (RECOMMENDED)

**Components:**

1. **Thrift Definitions** (`game.thrift`):
```thrift
enum TelemetryCounter {
    BYTES_RECEIVED = 1,
    BYTES_SENT = 2,
    SUCCESSFUL_REQUESTS = 3,
    ERROR_REQUESTS = 4,
}

struct TelemetrySnapshot {
    1: map<TelemetryCounter, i64> counters;
    2: i64 snapshot_timestamp_ms;
}

// Add to BaseService:
service BaseService {
    ServiceMetadata describe(),
    TelemetrySnapshot get_telemetry(),  // NEW
}
```

2. **TelemetryManager Class** (singleton):
```python
import threading
from typing import Dict
from game.ttypes import TelemetryCounter

class TelemetryManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._counters = {}
                    cls._instance._counter_lock = threading.Lock()
        return cls._instance

    def increment_counter(self, key: TelemetryCounter, amount: int) -> None:
        """Thread-safe counter increment."""
        with self._counter_lock:
            self._counters[key] = self._counters.get(key, 0) + amount

    def get_snapshot(self) -> Dict[TelemetryCounter, int]:
        """Get current counter values (lock-free read per requirements)."""
        return self._counters.copy()

    def reset_counters(self) -> None:
        """Reset all counters to zero."""
        with self._counter_lock:
            self._counters.clear()
```

3. **Integration into BaseServiceHandler**:
- Initialize TelemetryManager singleton in `__init__`
- Implement `get_telemetry()` endpoint
- Auto-instrument all service calls to track success/error

**Pros:**
- Simple, Pythonic approach using stdlib
- Lock-free reads (acceptable per requirements)
- Easy to test
- No background thread needed unless we want periodic tasks

**Cons:**
- Bytes tracking requires transport instrumentation (complex)
- Lock contention possible under very high load (but unlikely with simple increments)

### Approach 2: Multiprocessing.Value with Shared Memory

Use `multiprocessing.Value` for cross-process atomic counters.

**Pros:**
- Built-in atomic operations
- Could share telemetry across process boundaries

**Cons:**
- Services are already separate processes (each has own telemetry)
- Overkill for per-service counters
- More complex than needed

### Approach 3: Queue-Based Background Thread

Background thread consumes increment operations from a queue.

**Pros:**
- Lock-free for callers (just enqueue)
- Could batch updates
- Natural fit for "runs in own thread" requirement

**Cons:**
- More complex
- Adds latency for counter updates
- Unnecessary for simple integer increments

## Design Questions to Resolve

### 1. Bytes Tracking Implementation

**Options:**
- **A. Wrap Thrift transport layer** with custom instrumentation
- **B. Use Thrift's built-in transport stats** (if available)
- **C. Estimate from serialized request/response sizes**
- **D. Start simple**: Skip bytes initially, focus on request counters

**Recommendation**: Start with Option D, add bytes tracking in phase 2

### 2. Automatic Counter Updates

Should BaseServiceHandler automatically track request success/failure?

**Option A (Recommended)**: Wrap all service method calls with decorator/proxy:
```python
def _instrumented_call(self, method_name, handler_method, request):
    """Wrap service calls to auto-increment telemetry."""
    telemetry = TelemetryManager()
    try:
        response = handler_method(request)

        # Check if response indicates success or failure
        if hasattr(response, 'results') and response.results:
            if response.results[0].status == StatusType.SUCCESS:
                telemetry.increment_counter(TelemetryCounter.SUCCESSFUL_REQUESTS, 1)
            else:
                telemetry.increment_counter(TelemetryCounter.ERROR_REQUESTS, 1)

        return response
    except Exception as e:
        telemetry.increment_counter(TelemetryCounter.ERROR_REQUESTS, 1)
        raise
```

**Option B**: Require each service method to manually call `increment_counter()`

**Recommendation**: Option A for consistency and automation

### 3. Background Thread Necessity

**Question**: Do we actually need a background thread for the counter manager?

**Analysis**:
- Simple counter increments with locks don't require background thread
- Thread would be needed for:
  - Periodic metric flushing to external system
  - Computing derived metrics
  - Scheduled cleanup/rotation

**Options**:
- **A. No background thread**: TelemetryManager is just a data structure
- **B. Optional background thread**: Add later if needed for batch operations
- **C. Required background thread**: Start it in BaseServiceHandler init

**Recommendation**: Start with Option A (no thread), add if needed

### 4. Integration Test Service Choice

Which service to use for integration testing?

**Options**:
- ItemService (most mature, well-tested)
- InventoryService
- Create minimal test service

**Recommendation**: Use ItemService on port 9091

## Implementation Plan

### Phase 0: Fix Server Threading (MUST DO FIRST)

1. Update `run_servers.py` to use `TThreadPoolServer`
2. Test existing services work correctly with multi-threading
3. Verify db_models thread safety (connection pooling, etc.)
4. Run all existing tests to ensure no regressions

### Phase 1: Core Telemetry Infrastructure

1. Add telemetry enum and structs to `game.thrift`
2. Regenerate thrift code
3. Implement `TelemetryManager` class in `/vagrant/gamedb/thrift/py/services/telemetry.py`
4. Add unit tests for `TelemetryManager`

### Phase 2: BaseService Integration

1. Add `get_telemetry()` method to `BaseServiceHandler`
2. Implement automatic request counting (success/error)
3. Update service metadata for new endpoint
4. Add unit tests for telemetry endpoint

### Phase 3: Bytes Tracking (Optional/Future)

1. Research Thrift transport instrumentation
2. Implement custom transport wrapper if needed
3. Add bytes_sent/bytes_received tracking

### Phase 4: Integration Testing

1. Create integration test in `/vagrant/gamedb/thrift/py/services/tests/telemetry_integration_test.py`
2. Test should:
   - Spin up ItemService on dedicated port (e.g., 9999)
   - Make successful requests (create, load, list)
   - Make invalid requests (missing fields, bad IDs)
   - Call get_telemetry() endpoint
   - Verify counter values match expected requests
   - Clean up service process

## Recommended Path Forward

1. **FIRST**: Fix server threading model (Phase 0)
2. Implement Approach 1 (threading.Lock based)
3. Skip bytes tracking initially (add in Phase 3)
4. Use automatic request counting (Option A)
5. No background thread initially (Option A)
6. Integration test with ItemService

## Files to Modify/Create

### Modify:
- `/vagrant/gamedb/thrift/game.thrift` - Add telemetry definitions
- `/vagrant/gamedb/thrift/py/run_servers.py` - Update to TThreadPoolServer
- `/vagrant/gamedb/thrift/py/services/base_service.py` - Add get_telemetry(), auto-counting

### Create:
- `/vagrant/gamedb/thrift/py/services/telemetry.py` - TelemetryManager class
- `/vagrant/gamedb/thrift/py/services/tests/telemetry_test.py` - Unit tests
- `/vagrant/gamedb/thrift/py/services/tests/telemetry_integration_test.py` - Integration tests

## Notes

- Services run in separate processes, so each has independent telemetry
- Read operations don't need locks per requirements (eventual consistency OK)
- Client polls every 30-60 seconds, so slight delays acceptable
- Threading.Lock is sufficient for Python integer increments (no need for atomics)
