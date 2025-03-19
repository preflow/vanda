# Supabase Self-Hosting Project

This project provides a self-hosted Supabase setup using Docker Compose. Supabase is an open-source Firebase alternative that provides a suite of tools for building scalable and secure applications. This setup includes PostgreSQL, authentication, real-time subscriptions, storage, and more.

## Features

- **PostgreSQL Database**: A powerful, open-source relational database with logical replication enabled.
- **Authentication**: Secure user authentication with email/password, phone, and anonymous sign-in options.
- **Realtime Subscriptions**: Real-time updates using PostgreSQL's `LISTEN/NOTIFY` mechanism.
- **Storage**: File storage with support for image transformations.
- **API Gateway**: Kong API gateway for routing and managing API requests.
- **Analytics**: Logflare for logging and analytics.
- **Edge Functions**: Serverless functions for custom business logic.
- **Dashboard**: Supabase Studio for managing your database and services.

## Prerequisites

- Docker and Docker Compose installed on your machine.
- Basic understanding of Docker and environment variables.

## Configuration

### Environment Variables

The `.env` file contains all the necessary environment variables for configuring the Supabase services. Make sure to update the following variables before deploying to production:

- `POSTGRES_PASSWORD`: Password for the PostgreSQL database.
- `JWT_SECRET`: Secret key for signing JWTs.
- `ANON_KEY`: Public key for anonymous access.
- `SERVICE_ROLE_KEY`: Secret key for service-level access.
- `DASHBOARD_USERNAME` and `DASHBOARD_PASSWORD`: Credentials for accessing the Supabase dashboard.
- `SECRET_KEY_BASE`: Secret key base for encryption.
- `VAULT_ENC_KEY`: Encryption key for the vault.

### Ports

The following ports are exposed by the services:

- **Kong API Gateway**: 
  - HTTP: `8000`
  - HTTPS: `8443`
- **Supabase Studio**: `3000`
- **Analytics (Logflare)**: `4000`
- **PostgreSQL Database**: `5432`
- **Supavisor Pooler**: 
  - PostgreSQL: `5432`
  - Transaction Pooler: `6543`

## Running the Project

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/supabase-self-hosted.git
   cd supabase-self-hosted
   ```

2. **Update the `.env` file**:
   Modify the `.env` file to set your desired configuration values.

3. **Start the services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the services**:
   - **Supabase Studio**: Open `http://localhost:3000` in your browser.
   - **API Gateway**: Access the API at `http://localhost:8000`.
   - **Analytics**: Access Logflare at `http://localhost:4000`.

## Stopping the Project

To stop the services, run:
```bash
docker-compose down
```

To stop and remove all volumes (including the database data), run:
```bash
docker-compose down -v --remove-orphans
```

## Resetting the Project

To reset everything (including the database), run:
```bash
./reset.sh
```

## Customization

### Using an External PostgreSQL Database

If you want to use an external PostgreSQL database, update the `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` variables in the `.env` file. Additionally, comment out the `db` service in the `docker-compose.yml` file.

### Enabling BigQuery for Analytics

To use BigQuery as the backend for analytics, uncomment the relevant sections in the `docker-compose.yml` file and provide the necessary Google Cloud credentials.

### Adding Custom Edge Functions

Place your custom edge functions in the `./volumes/functions` directory. The functions will be automatically loaded by the `functions` service.

## Troubleshooting

- **Health Checks**: Ensure all services are healthy by checking the logs:
  ```bash
  docker-compose logs
  ```
- **Port Conflicts**: If you encounter port conflicts, update the port mappings in the `docker-compose.yml` file.
- **Database Issues**: If the database fails to start, check the logs and ensure the `POSTGRES_PASSWORD` is correctly set.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

This README provides a comprehensive guide to setting up and running a self-hosted Supabase instance. For more detailed documentation, refer to the [Supabase official documentation](https://supabase.com/docs).
