#!/bin/bash
# run_sql_queries.sh

# Configuration
DB_HOST="dbase.cs.jhu.edu"
DB_USER="FA25_ycao73"
DB_NAME="FA25_ycao73_db"
SQL_FILE="3-sql-tasks.sql"
LOG_FILE="query_results_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting SQL Query Execution${NC}"
echo "=================================="
echo "Database: $DB_HOST/$DB_NAME"
echo "SQL File: $SQL_FILE"
echo "Log File: $LOG_FILE"
echo "Started at: $(date)"
echo "=================================="

# Check if SQL file exists
if [ ! -f "$SQL_FILE" ]; then
    echo -e "${RED}❌ Error: SQL file '$SQL_FILE' not found!${NC}"
    exit 1
fi

# Prompt for password
echo -n "Enter database password: "
read -s DB_PASSWORD
echo

# Create log file with header
cat > "$LOG_FILE" << EOF
=================================================================
Materials Project Database Query Results
=================================================================
Database: $DB_HOST/$DB_NAME
SQL File: $SQL_FILE
Execution Date: $(date)
=================================================================

EOF

# Execute SQL with logging
echo -e "${YELLOW}📊 Executing SQL queries...${NC}"

mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" \
    --table \
    --verbose \
    --show-warnings \
    < "$SQL_FILE" >> "$LOG_FILE" 2>&1

# Check execution status
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ SQL execution completed successfully!${NC}"
    echo "Results saved to: $LOG_FILE"
    
    # Show summary
    echo -e "\n${YELLOW}📋 Execution Summary:${NC}"
    echo "Log file size: $(du -h "$LOG_FILE" | cut -f1)"
    echo "Total lines: $(wc -l < "$LOG_FILE")"
    
    # Show first few lines of results
    echo -e "\n${YELLOW}📖 Preview of results:${NC}"
    head -30 "$LOG_FILE"
    echo "..."
    echo "(See full results in $LOG_FILE)"
    
else
    echo -e "${RED}❌ SQL execution failed!${NC}"
    echo "Check the log file for errors: $LOG_FILE"
    tail -20 "$LOG_FILE"
fi

echo -e "\n${GREEN}🏁 Execution completed at: $(date)${NC}"