#!/bin/bash
set -euo pipefail

php /update.php
exec docker-php-entrypoint apache2-foreground

