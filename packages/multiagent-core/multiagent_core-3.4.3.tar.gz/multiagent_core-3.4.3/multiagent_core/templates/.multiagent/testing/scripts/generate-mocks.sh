#!/bin/bash

# Mock & Stub Generation Script
# Generates mock implementations for testing based on spec analysis

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Arguments
SPEC_DIR="${1:-specs/001-feature}"
OUTPUT_DIR="${2:-tests}"
VERBOSE="${3:-false}"

echo -e "${BLUE}=== Mock & Stub Generation ===${NC}"
echo "Spec: $SPEC_DIR"
echo "Output: $OUTPUT_DIR"
echo ""

# Ensure output directories exist
mkdir -p "$OUTPUT_DIR"/backend/mocks
mkdir -p "$OUTPUT_DIR"/frontend/mocks

# Function to detect required mocks from spec
detect_required_mocks() {
    local spec_file="$1"
    local mocks=""

    # Database mocks
    if grep -qi "database\|postgres\|mysql\|mongodb" "$spec_file" 2>/dev/null; then
        mocks="$mocks database"
    fi

    # API mocks
    if grep -qi "api\|endpoint\|REST\|GraphQL" "$spec_file" 2>/dev/null; then
        mocks="$mocks api"
    fi

    # Auth mocks
    if grep -qi "auth\|login\|jwt\|session" "$spec_file" 2>/dev/null; then
        mocks="$mocks auth"
    fi

    # External service mocks
    if grep -qi "stripe\|paypal\|sendgrid\|twilio\|s3\|aws" "$spec_file" 2>/dev/null; then
        mocks="$mocks external"
    fi

    # Cache mocks
    if grep -qi "redis\|cache\|memcached" "$spec_file" 2>/dev/null; then
        mocks="$mocks cache"
    fi

    # Message queue mocks
    if grep -qi "queue\|rabbitmq\|kafka\|sqs" "$spec_file" 2>/dev/null; then
        mocks="$mocks queue"
    fi

    echo "$mocks"
}

# Generate database mock
generate_database_mock() {
    echo -e "${YELLOW}Generating database mock...${NC}"

    cat > "$OUTPUT_DIR/backend/mocks/db.mock.js" << 'EOF'
// Database Mock
class MockDatabase {
    constructor() {
        this.data = new Map();
        this.queries = [];
    }

    async query(sql, params = []) {
        this.queries.push({ sql, params, timestamp: Date.now() });
        return { rows: [], rowCount: 0 };
    }

    async findOne(collection, query) {
        const key = `${collection}:${JSON.stringify(query)}`;
        return this.data.get(key) || null;
    }

    async insert(collection, data) {
        const id = Math.random().toString(36);
        const key = `${collection}:${id}`;
        this.data.set(key, { ...data, id });
        return { id };
    }

    async update(collection, query, data) {
        // Mock update
        return { modifiedCount: 1 };
    }

    reset() {
        this.data.clear();
        this.queries = [];
    }

    getQueries() {
        return this.queries;
    }
}

module.exports = { MockDatabase };
EOF

    echo -e "  ${GREEN}✓${NC} Database mock created"
}

# Generate API mock
generate_api_mock() {
    echo -e "${YELLOW}Generating API mock...${NC}"

    cat > "$OUTPUT_DIR/backend/mocks/api.mock.js" << 'EOF'
// API Mock
class MockAPI {
    constructor() {
        this.endpoints = new Map();
        this.requests = [];
    }

    register(method, path, handler) {
        const key = `${method}:${path}`;
        this.endpoints.set(key, handler);
    }

    async request(method, path, data = {}) {
        const key = `${method}:${path}`;
        const handler = this.endpoints.get(key);

        this.requests.push({ method, path, data, timestamp: Date.now() });

        if (!handler) {
            throw new Error(`No mock registered for ${method} ${path}`);
        }

        return handler(data);
    }

    reset() {
        this.endpoints.clear();
        this.requests = [];
    }

    getRequests() {
        return this.requests;
    }
}

module.exports = { MockAPI };
EOF

    echo -e "  ${GREEN}✓${NC} API mock created"
}

# Generate auth mock
generate_auth_mock() {
    echo -e "${YELLOW}Generating auth mock...${NC}"

    cat > "$OUTPUT_DIR/backend/mocks/auth.mock.js" << 'EOF'
// Auth Mock
class MockAuth {
    constructor() {
        this.users = new Map();
        this.sessions = new Map();
    }

    async register(email, password) {
        if (this.users.has(email)) {
            throw new Error('User already exists');
        }

        const user = {
            id: Math.random().toString(36),
            email,
            password, // In real code, this would be hashed
            createdAt: new Date()
        };

        this.users.set(email, user);
        return { user: { id: user.id, email: user.email } };
    }

    async login(email, password) {
        const user = this.users.get(email);
        if (!user || user.password !== password) {
            throw new Error('Invalid credentials');
        }

        const token = `mock-token-${Math.random().toString(36)}`;
        this.sessions.set(token, user);

        return { token, user: { id: user.id, email: user.email } };
    }

    async verify(token) {
        const user = this.sessions.get(token);
        if (!user) {
            throw new Error('Invalid token');
        }
        return { user: { id: user.id, email: user.email } };
    }

    reset() {
        this.users.clear();
        this.sessions.clear();
    }
}

module.exports = { MockAuth };
EOF

    echo -e "  ${GREEN}✓${NC} Auth mock created"
}

# Generate external service mock
generate_external_mock() {
    echo -e "${YELLOW}Generating external service mock...${NC}"

    cat > "$OUTPUT_DIR/backend/mocks/external.mock.js" << 'EOF'
// External Service Mock
class MockExternalService {
    constructor(serviceName) {
        this.serviceName = serviceName;
        this.calls = [];
        this.responses = new Map();
    }

    setResponse(method, response) {
        this.responses.set(method, response);
    }

    async call(method, params = {}) {
        this.calls.push({ method, params, timestamp: Date.now() });

        const response = this.responses.get(method);
        if (!response) {
            throw new Error(`No mock response for ${this.serviceName}.${method}`);
        }

        return typeof response === 'function' ? response(params) : response;
    }

    getCalls() {
        return this.calls;
    }

    reset() {
        this.calls = [];
    }
}

// Pre-configured service mocks
const createStripeMock = () => {
    const stripe = new MockExternalService('Stripe');
    stripe.setResponse('createCharge', () => ({ id: 'ch_mock', status: 'succeeded' }));
    stripe.setResponse('createCustomer', () => ({ id: 'cus_mock' }));
    return stripe;
};

const createSendGridMock = () => {
    const sendgrid = new MockExternalService('SendGrid');
    sendgrid.setResponse('send', () => ({ messageId: 'msg_mock', status: 'sent' }));
    return sendgrid;
};

module.exports = { MockExternalService, createStripeMock, createSendGridMock };
EOF

    echo -e "  ${GREEN}✓${NC} External service mock created"
}

# Generate cache mock
generate_cache_mock() {
    echo -e "${YELLOW}Generating cache mock...${NC}"

    cat > "$OUTPUT_DIR/backend/mocks/cache.mock.js" << 'EOF'
// Cache Mock
class MockCache {
    constructor() {
        this.store = new Map();
        this.hits = 0;
        this.misses = 0;
    }

    async get(key) {
        const value = this.store.get(key);
        if (value !== undefined) {
            this.hits++;
            return value;
        }
        this.misses++;
        return null;
    }

    async set(key, value, ttl = 0) {
        this.store.set(key, value);
        if (ttl > 0) {
            setTimeout(() => this.store.delete(key), ttl * 1000);
        }
        return true;
    }

    async delete(key) {
        return this.store.delete(key);
    }

    async flush() {
        this.store.clear();
        this.hits = 0;
        this.misses = 0;
    }

    getStats() {
        return {
            hits: this.hits,
            misses: this.misses,
            hitRate: this.hits / (this.hits + this.misses) || 0,
            size: this.store.size
        };
    }
}

module.exports = { MockCache };
EOF

    echo -e "  ${GREEN}✓${NC} Cache mock created"
}

# Generate message queue mock
generate_queue_mock() {
    echo -e "${YELLOW}Generating message queue mock...${NC}"

    cat > "$OUTPUT_DIR/backend/mocks/queue.mock.js" << 'EOF'
// Message Queue Mock
class MockQueue {
    constructor() {
        this.queues = new Map();
        this.handlers = new Map();
        this.messages = [];
    }

    async publish(queueName, message) {
        if (!this.queues.has(queueName)) {
            this.queues.set(queueName, []);
        }

        const msg = {
            id: Math.random().toString(36),
            queue: queueName,
            data: message,
            timestamp: Date.now()
        };

        this.queues.get(queueName).push(msg);
        this.messages.push(msg);

        // Trigger handler if registered
        const handler = this.handlers.get(queueName);
        if (handler) {
            setImmediate(() => handler(message));
        }

        return msg.id;
    }

    async subscribe(queueName, handler) {
        this.handlers.set(queueName, handler);
    }

    async getMessages(queueName) {
        return this.queues.get(queueName) || [];
    }

    reset() {
        this.queues.clear();
        this.handlers.clear();
        this.messages = [];
    }

    getAllMessages() {
        return this.messages;
    }
}

module.exports = { MockQueue };
EOF

    echo -e "  ${GREEN}✓${NC} Message queue mock created"
}

# Main execution
echo -e "${YELLOW}Analyzing spec for required mocks...${NC}"

if [[ -f "$SPEC_DIR/spec.md" ]]; then
    REQUIRED_MOCKS=$(detect_required_mocks "$SPEC_DIR/spec.md")
elif [[ -f "$SPEC_DIR/plan.md" ]]; then
    REQUIRED_MOCKS=$(detect_required_mocks "$SPEC_DIR/plan.md")
else
    echo -e "${RED}No spec files found in $SPEC_DIR${NC}"
    exit 1
fi

echo -e "Required mocks: ${BLUE}${REQUIRED_MOCKS:-none}${NC}"
echo ""

# Generate mocks based on detection
for mock in $REQUIRED_MOCKS; do
    case $mock in
        database)
            generate_database_mock
            ;;
        api)
            generate_api_mock
            ;;
        auth)
            generate_auth_mock
            ;;
        external)
            generate_external_mock
            ;;
        cache)
            generate_cache_mock
            ;;
        queue)
            generate_queue_mock
            ;;
    esac
done

# Generate index file
echo -e "${YELLOW}Creating mock index...${NC}"
cat > "$OUTPUT_DIR/backend/mocks/index.js" << 'EOF'
// Mock Index - Export all mocks
const fs = require('fs');
const path = require('path');

const mocks = {};

// Load all mock files
fs.readdirSync(__dirname)
    .filter(file => file.endsWith('.mock.js'))
    .forEach(file => {
        const mockName = file.replace('.mock.js', '');
        mocks[mockName] = require(`./${file}`);
    });

module.exports = mocks;
EOF

echo -e "  ${GREEN}✓${NC} Mock index created"
echo ""

# Generate mock usage example
echo -e "${YELLOW}Creating usage example...${NC}"
cat > "$OUTPUT_DIR/backend/mocks/README.md" << 'EOF'
# Mock Usage Guide

## Available Mocks

Generated mocks based on spec analysis. Use these in your tests to isolate components.

### Database Mock
```javascript
const { MockDatabase } = require('./mocks/db.mock');
const db = new MockDatabase();

// Use in tests
await db.insert('users', { name: 'Test User' });
const queries = db.getQueries(); // Get all executed queries
db.reset(); // Clear data between tests
```

### API Mock
```javascript
const { MockAPI } = require('./mocks/api.mock');
const api = new MockAPI();

// Register handlers
api.register('GET', '/users/:id', (data) => ({ id: data.id, name: 'Test' }));

// Use in tests
const result = await api.request('GET', '/users/:id', { id: 1 });
```

### Auth Mock
```javascript
const { MockAuth } = require('./mocks/auth.mock');
const auth = new MockAuth();

// Test authentication flow
await auth.register('test@example.com', 'password');
const { token } = await auth.login('test@example.com', 'password');
await auth.verify(token);
```

### External Service Mocks
```javascript
const { createStripeMock } = require('./mocks/external.mock');
const stripe = createStripeMock();

// Use in tests
const charge = await stripe.call('createCharge', { amount: 1000 });
const calls = stripe.getCalls(); // Verify calls made
```

## Best Practices

1. **Reset mocks between tests** to ensure isolation
2. **Verify mock calls** to ensure expected interactions
3. **Use dependency injection** to swap real services with mocks
4. **Keep mocks simple** - they should simulate behavior, not reimplement logic

## Integration with Test Framework

```javascript
beforeEach(() => {
    // Reset all mocks
    db.reset();
    api.reset();
    auth.reset();
});

afterEach(() => {
    // Verify expectations if needed
});
```
EOF

echo -e "  ${GREEN}✓${NC} Usage guide created"
echo ""

echo -e "${GREEN}=== Mock Generation Complete ===${NC}"
echo "Generated mocks in: $OUTPUT_DIR/backend/mocks/"
echo "Run tests with: npm test or pytest"