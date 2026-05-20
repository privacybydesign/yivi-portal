#!/bin/sh

export > /etc/env_vars.sh
cat > /etc/cron.d/cron-schedule <<'EOF'
*/5 * * * * root . /etc/env_vars.sh && /usr/local/bin/python /app/manage.py run_crons new_dns >> /var/log/cron.log 2>&1
0 1 * * * root . /etc/env_vars.sh && /usr/local/bin/python /app/manage.py run_crons existing_dns >> /var/log/cron.log 2>&1
0 */12 * * * root . /etc/env_vars.sh && /usr/local/bin/python /app/manage.py run_crons trusted_aps >> /var/log/cron.log 2>&1
0 */12 * * * root . /etc/env_vars.sh && /usr/local/bin/python /app/manage.py run_crons trusted_rps >> /var/log/cron.log 2>&1
EOF
chmod 0644 /etc/cron.d/cron-schedule
crontab /etc/cron.d/cron-schedule
touch /var/log/cron.log

# Start cron in the background
cron

# Tail the cron log to keep the container running
tail -f /var/log/cron.log
