#!/bin/bash
# OpenFinOps Test Runner
# Usage: ./run_tests.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 OpenFinOps Test Suite"
echo "========================"

# Parse command line arguments
TEST_TYPE="${1:-all}"
COVERAGE="${2:-yes}"

case "$TEST_TYPE" in
  unit)
    echo -e "${YELLOW}Running unit tests...${NC}"
    pytest -v -m unit --tb=short
    ;;
  integration)
    echo -e "${YELLOW}Running integration tests...${NC}"
    pytest -v -m integration --tb=short
    ;;
  visualization)
    echo -e "${YELLOW}Running visualization tests...${NC}"
    pytest -v -m visualization --tb=short
    ;;
  fast)
    echo -e "${YELLOW}Running fast tests (excluding slow)...${NC}"
    pytest -v -m "not slow" --tb=short
    ;;
  coverage)
    echo -e "${YELLOW}Running tests with coverage report...${NC}"
    pytest -v --cov=src/openfinops --cov-report=term-missing --cov-report=html
    echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
    ;;
  all)
    if [ "$COVERAGE" = "yes" ]; then
      echo -e "${YELLOW}Running all tests with coverage...${NC}"
      pytest -v --cov=src/openfinops --cov-report=term-missing --cov-report=html --cov-report=xml
      echo -e "${GREEN}✅ All tests completed${NC}"
      echo -e "${GREEN}Coverage report: htmlcov/index.html${NC}"
    else
      echo -e "${YELLOW}Running all tests without coverage...${NC}"
      pytest -v
      echo -e "${GREEN}✅ All tests completed${NC}"
    fi
    ;;
  quick)
    echo -e "${YELLOW}Running quick smoke tests...${NC}"
    pytest -v -m unit --tb=short -x  # Stop on first failure
    ;;
  *)
    echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
    echo "Usage: ./run_tests.sh [unit|integration|visualization|fast|coverage|all|quick]"
    exit 1
    ;;
esac

echo ""
echo -e "${GREEN}✨ Test run complete!${NC}"
