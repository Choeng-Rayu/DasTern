#!/bin/bash

#########################################
# DasTern Database Setup Script - Fedora
# Both CLI and Docker options
#########################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Menu
show_menu() {
    print_header "DasTern Database Setup Options"
    echo "Choose setup method:"
    echo "1. Docker Compose (Recommended - Easiest)"
    echo "2. Native PostgreSQL (System-wide installation)"
    echo "3. Exit"
    echo ""
    read -p "Enter your choice (1-3): " choice
}

#########################################
# OPTION 1: DOCKER COMPOSE SETUP
#########################################
setup_docker() {
    print_header "Docker Compose PostgreSQL Setup"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        print_info "Install Docker from: https://docs.docker.com/engine/install/"
        return 1
    fi
    
    # Check if docker-compose is installed
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        return 1
    fi
    
    print_success "Docker detected"
    
    # Read environment variables from .env or set defaults
    if [ -f .env ]; then
        print_info "Reading existing .env file"
        source .env
    fi
    
    # Set defaults if not set
    DB_USER=${DB_USER:-"dastern"}
    DB_PASSWORD=${DB_PASSWORD:-"dastern_secure_password_2026"}
    DB_NAME=${DB_NAME:-"dastern"}
    DB_PORT=${DB_PORT:-"5432"}
    
    print_info "Database Configuration:"
    echo "  Username: $DB_USER"
    echo "  Database: $DB_NAME"
    echo "  Port: $DB_PORT"
    echo ""
    
    read -p "Continue with above settings? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Setup cancelled"
        return 1
    fi
    
    # Start Docker compose
    print_info "Starting Docker containers..."
    docker-compose up -d postgres
    
    sleep 5
    
    # Wait for PostgreSQL to be ready
    print_info "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if docker-compose exec -T postgres pg_isready -U $DB_USER &> /dev/null; then
            print_success "PostgreSQL is ready!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "PostgreSQL failed to start"
            return 1
        fi
        echo -n "."
        sleep 1
    done
    
    # Import schema
    print_info "Importing database schema..."
    docker-compose exec -T postgres psql -U $DB_USER -d $DB_NAME < database/schema.sql
    
    print_success "Docker setup completed!"
    print_info "Connection details:"
    echo "  Host: localhost"
    echo "  Port: $DB_PORT"
    echo "  Database: $DB_NAME"
    echo "  Username: $DB_USER"
    echo "  Password: $DB_PASSWORD"
}

#########################################
# OPTION 2: NATIVE POSTGRESQL SETUP
#########################################
setup_native() {
    print_header "Native PostgreSQL Setup"
    
    # Check if PostgreSQL is installed
    if ! command -v psql &> /dev/null; then
        print_warning "PostgreSQL not found. Installing..."
        sudo dnf install -y postgresql postgresql-server postgresql-contrib
        print_success "PostgreSQL installed"
    else
        print_success "PostgreSQL detected"
    fi
    
    # Initialize database if needed
    if [ ! -d "/var/lib/pgsql/data/base" ]; then
        print_info "Initializing PostgreSQL database..."
        sudo postgresql-setup initdb
    fi
    
    # Start and enable PostgreSQL
    print_info "Starting PostgreSQL service..."
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    sleep 2
    
    # Check status
    if sudo systemctl is-active --quiet postgresql; then
        print_success "PostgreSQL service is running"
    else
        print_error "PostgreSQL service failed to start"
        return 1
    fi
    
    # Configure credentials
    print_info "Configuring database user and database..."
    
    DB_USER="dastern"
    DB_PASSWORD="dastern_secure_password_2026"
    DB_NAME="dastern"
    
    read -p "Enter database username [$DB_USER]: " input_user
    DB_USER=${input_user:-$DB_USER}
    
    read -sp "Enter database password [$DB_PASSWORD]: " input_pass
    echo
    DB_PASSWORD=${input_pass:-$DB_PASSWORD}
    
    # Create user and database
    print_info "Creating database user and database..."
    sudo -u postgres psql << EOF
-- Create user if not exists
DO \$\$
BEGIN
    CREATE USER "$DB_USER" WITH PASSWORD '$DB_PASSWORD';
EXCEPTION WHEN duplicate_object THEN
    ALTER USER "$DB_USER" WITH PASSWORD '$DB_PASSWORD';
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE "$DB_NAME"'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE "$DB_NAME" TO "$DB_USER";
EOF
    
    print_success "User and database created"
    
    # Update pg_hba.conf for md5 authentication
    print_info "Configuring authentication..."
    sudo cp /var/lib/pgsql/data/pg_hba.conf /var/lib/pgsql/data/pg_hba.conf.backup
    
    # Update local connection to md5 (or scram-sha-256 for newer versions)
    sudo sed -i 's/^local   all             all                                     peer$/local   all             all                                     md5/' /var/lib/pgsql/data/pg_hba.conf
    
    # Reload PostgreSQL configuration
    sudo systemctl reload postgresql
    
    print_success "Authentication configured"
    
    # Import schema
    print_info "Importing database schema..."
    PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USER" -d "$DB_NAME" -h localhost < database/schema.sql
    
    if [ $? -eq 0 ]; then
        print_success "Schema imported successfully"
    else
        print_error "Failed to import schema"
        return 1
    fi
    
    print_success "Native PostgreSQL setup completed!"
    print_info "Connection details:"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  Database: $DB_NAME"
    echo "  Username: $DB_USER"
    echo "  Password: $DB_PASSWORD"
    
    # Save to .env
    read -p "Save credentials to .env file? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cat >> .env << EOF

# Database Configuration
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_NAME=$DB_NAME
DB_PORT=5432
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
EOF
        print_success "Credentials saved to .env"
    fi
}

#########################################
# TEST CONNECTION
#########################################
test_connection() {
    print_header "Testing Database Connection"
    
    read -p "Enter host (default: localhost): " host
    host=${host:-"localhost"}
    
    read -p "Enter port (default: 5432): " port
    port=${port:-"5432"}
    
    read -p "Enter database (default: dastern): " db
    db=${db:-"dastern"}
    
    read -p "Enter username (default: dastern): " user
    user=${user:-"dastern"}
    
    read -sp "Enter password: " pass
    echo
    
    print_info "Testing connection..."
    
    if PGPASSWORD="$pass" psql -h "$host" -p "$port" -U "$user" -d "$db" -c "SELECT version();" &> /dev/null; then
        print_success "Connection successful!"
        PGPASSWORD="$pass" psql -h "$host" -p "$port" -U "$user" -d "$db" -c "SELECT version();"
    else
        print_error "Connection failed!"
        print_info "Verify your credentials and try again"
    fi
}

#########################################
# DBEAVER SETUP GUIDE
#########################################
show_dbeaver_guide() {
    print_header "DBeaver GUI Setup Guide"
    
    cat << 'EOF'

📌 DBEAVER CONNECTION SETUP STEPS:

1. Open DBeaver
2. Click "Database" → "New Database Connection"
3. Select "PostgreSQL" → Click "Next"

4. Fill in Connection Settings:
   ├─ Server Host: localhost
   ├─ Port: 5432
   ├─ Database: dastern
   ├─ Username: dastern
   ├─ Password: (your password)
   └─ Save password locally: ✓ (checked)

5. Click "Test Connection"
   - If successful: Green checkmark appears
   - If failed: Check credentials above

6. Click "Finish"

7. Import Schema:
   ├─ Right-click "dastern" database
   ├─ Select "SQL Editor" → "Open SQL Script"
   ├─ Select: database/schema.sql
   ├─ Press Ctrl+Enter to execute
   └─ Check "Console" for any errors

✅ Done! Your database is ready.

EOF
    
    read -p "Press Enter to continue..."
}

#########################################
# MAIN MENU LOOP
#########################################
main() {
    print_header "Welcome to DasTern Database Setup"
    
    while true; do
        show_menu
        
        case $choice in
            1)
                setup_docker
                ;;
            2)
                setup_native
                ;;
            3)
                print_info "Exiting setup..."
                exit 0
                ;;
            *)
                print_error "Invalid choice"
                ;;
        esac
        
        echo ""
        read -p "Do you want to test the connection? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            test_connection
        fi
        
        read -p "Do you want to see DBeaver setup guide? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            show_dbeaver_guide
        fi
        
        read -p "Setup another database or option? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_success "Setup complete! Happy coding! 🚀"
            exit 0
        fi
    done
}

# Run main
main
